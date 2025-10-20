"""Output normalization and export for Oroitz."""

import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from oroitz.core.telemetry import logger


class ProcessInfo(BaseModel):
    """Normalized process information."""

    pid: int = Field(..., ge=0, description="Process ID must be non-negative")
    name: str = Field(..., min_length=1, description="Process name cannot be empty")
    ppid: Optional[int] = Field(None, ge=0)
    threads: Optional[int] = Field(None, ge=0)
    handles: Optional[int] = Field(None, ge=0)
    session: Optional[int] = Field(None, ge=0)
    wow64: Optional[bool] = None
    create_time: Optional[str] = None
    exit_time: Optional[str] = None
    anomalies: List[str] = Field(default_factory=list)

    @field_validator("pid", "ppid", "threads", "handles", "session")
    @classmethod
    def validate_non_negative(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 0:
            raise ValueError("Value must be non-negative")
        return v


class NetworkConnection(BaseModel):
    """Normalized network connection information."""

    offset: Optional[str] = None
    pid: Optional[int] = Field(None, ge=0)
    owner: Optional[str] = None
    created: Optional[str] = None
    local_addr: Optional[str] = None
    remote_addr: Optional[str] = None
    state: Optional[str] = None

    @field_validator("pid")
    @classmethod
    def validate_pid(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 0:
            raise ValueError("PID must be non-negative")
        return v


class MalfindHit(BaseModel):
    """Normalized malfind hit information."""

    pid: Optional[int] = Field(None, ge=0)
    process_name: Optional[str] = None
    start: Optional[str] = None
    end: Optional[str] = None
    tag: Optional[str] = None
    protection: Optional[str] = None
    commit_charge: Optional[int] = Field(None, ge=0)
    private_memory: Optional[int] = Field(None, ge=0)

    @field_validator("pid", "commit_charge", "private_memory")
    @classmethod
    def validate_non_negative(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 0:
            raise ValueError("Value must be non-negative")
        return v


class QuickTriageOutput(BaseModel):
    """Output for quick_triage workflow."""

    processes: List[ProcessInfo] = Field(default_factory=list)
    network_connections: List[NetworkConnection] = Field(default_factory=list)
    malfind_hits: List[MalfindHit] = Field(default_factory=list)


class OutputNormalizer:
    """Normalizes plugin outputs to structured schemas."""

    def normalize_pslist(self, raw_output: List[Dict[str, Any]]) -> List[ProcessInfo]:
        """Normalize pslist output."""
        normalized: List[ProcessInfo] = []
        for item in raw_output:
            # Basic normalization - in real implementation, would handle various formats
            process = ProcessInfo(
                pid=int(item.get("pid", 0)),
                name=str(item.get("name", "")),
                ppid=item.get("ppid"),
                threads=item.get("threads"),
                handles=item.get("handles"),
                session=item.get("session"),
                wow64=item.get("wow64"),
                create_time=item.get("create_time"),
                exit_time=item.get("exit_time"),
            )
            normalized.append(process)
        return normalized

    def normalize_netscan(self, raw_output: List[Dict[str, Any]]) -> List[NetworkConnection]:
        """Normalize netscan output."""
        normalized: List[NetworkConnection] = []
        for item in raw_output:
            conn = NetworkConnection(
                offset=item.get("offset"),
                pid=item.get("pid"),
                owner=item.get("owner"),
                created=item.get("created"),
                local_addr=item.get("local_addr"),
                remote_addr=item.get("remote_addr"),
                state=item.get("state"),
            )
            normalized.append(conn)
        return normalized

    def normalize_malfind(self, raw_output: List[Dict[str, Any]]) -> List[MalfindHit]:
        """Normalize malfind output."""
        normalized: List[MalfindHit] = []
        for item in raw_output:
            hit = MalfindHit(
                pid=item.get("pid"),
                process_name=item.get("process_name"),
                start=item.get("start"),
                end=item.get("end"),
                tag=item.get("tag"),
                protection=item.get("protection"),
                commit_charge=item.get("commit_charge"),
                private_memory=item.get("private_memory"),
            )
            normalized.append(hit)
        return normalized

    def normalize_quick_triage(self, results: List) -> QuickTriageOutput:
        """Normalize complete quick_triage workflow output."""
        output = QuickTriageOutput()

        for result in results:
            if result.plugin_name == "windows.pslist" and result.output:
                output.processes = self.normalize_pslist(result.output)
            elif result.plugin_name == "windows.netscan" and result.output:
                output.network_connections = self.normalize_netscan(result.output)
            elif result.plugin_name == "windows.malfind" and result.output:
                output.malfind_hits = self.normalize_malfind(result.output)

        return output


class OutputExporter:
    """Exports normalized outputs to various formats."""

    def export_json(self, output: BaseModel, path: Path) -> None:
        """Export to JSON."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(output.model_dump(), f, indent=2, ensure_ascii=False)
        logger.info(f"Exported to JSON: {path}")

    def export_csv(self, output: BaseModel, path: Path) -> None:
        """Export to CSV."""
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if isinstance(output, QuickTriageOutput):
            # Export each section to separate CSV files
            base_path = path.with_suffix('')
            
            # Processes
            if output.processes:
                processes_path = Path(f"{base_path}_processes.csv")
                with open(processes_path, 'w', newline='', encoding='utf-8') as f:
                    if output.processes:
                        writer = csv.DictWriter(f, fieldnames=output.processes[0].model_dump().keys())
                        writer.writeheader()
                        for item in output.processes:
                            writer.writerow(item.model_dump())
                logger.info(f"Exported processes to CSV: {processes_path}")
            
            # Network connections
            if output.network_connections:
                net_path = Path(f"{base_path}_network.csv")
                with open(net_path, 'w', newline='', encoding='utf-8') as f:
                    if output.network_connections:
                        writer = csv.DictWriter(f, fieldnames=output.network_connections[0].model_dump().keys())
                        writer.writeheader()
                        for item in output.network_connections:
                            writer.writerow(item.model_dump())
                logger.info(f"Exported network connections to CSV: {net_path}")
            
            # Malfind hits
            if output.malfind_hits:
                malfind_path = Path(f"{base_path}_malfind.csv")
                with open(malfind_path, 'w', newline='', encoding='utf-8') as f:
                    if output.malfind_hits:
                        writer = csv.DictWriter(f, fieldnames=output.malfind_hits[0].model_dump().keys())
                        writer.writeheader()
                        for item in output.malfind_hits:
                            writer.writerow(item.model_dump())
                logger.info(f"Exported malfind hits to CSV: {malfind_path}")
        else:
            # Generic export for other models
            with open(path, 'w', newline='', encoding='utf-8') as f:
                data = output.model_dump()
                if isinstance(data, dict):
                    writer = csv.DictWriter(f, fieldnames=data.keys())
                    writer.writeheader()
                    writer.writerow(data)
                elif isinstance(data, list) and data:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
            logger.info(f"Exported to CSV: {path}")

    def export_parquet(self, output: BaseModel, path: Path) -> None:
        """Export to Parquet (placeholder)."""
        logger.info(f"Parquet export not implemented yet: {path}")
