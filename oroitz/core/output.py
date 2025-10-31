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

    def __init__(
        self,
        pid: int,
        name: str,
        ppid: Optional[int] = None,
        threads: Optional[int] = None,
        handles: Optional[int] = None,
        session: Optional[int] = None,
        wow64: Optional[bool] = None,
        create_time: Optional[str] = None,
        exit_time: Optional[str] = None,
        anomalies: Optional[List[str]] = None,
    ) -> None:
        super().__init__(
            pid=pid,
            name=name,
            ppid=ppid,
            threads=threads,
            handles=handles,
            session=session,
            wow64=wow64,
            create_time=create_time,
            exit_time=exit_time,
            anomalies=anomalies or [],
        )


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

    def __init__(
        self,
        offset: Optional[str] = None,
        pid: Optional[int] = None,
        owner: Optional[str] = None,
        created: Optional[str] = None,
        local_addr: Optional[str] = None,
        remote_addr: Optional[str] = None,
        state: Optional[str] = None,
    ) -> None:
        super().__init__(
            offset=offset,
            pid=pid,
            owner=owner,
            created=created,
            local_addr=local_addr,
            remote_addr=remote_addr,
            state=state,
        )


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

    def __init__(
        self,
        pid: Optional[int] = None,
        process_name: Optional[str] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
        tag: Optional[str] = None,
        protection: Optional[str] = None,
        commit_charge: Optional[int] = None,
        private_memory: Optional[int] = None,
    ) -> None:
        super().__init__(
            pid=pid,
            process_name=process_name,
            start=start,
            end=end,
            tag=tag,
            protection=protection,
            commit_charge=commit_charge,
            private_memory=private_memory,
        )


class UserInfo(BaseModel):
    """Normalized user information from Windows SIDs."""

    name: Optional[str] = None
    sid: Optional[str] = None
    pid: Optional[int] = Field(None, ge=0)
    process: Optional[str] = None

    @field_validator("pid")
    @classmethod
    def validate_non_negative(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 0:
            raise ValueError("Value must be non-negative")
        return v

    def __init__(
        self,
        name: Optional[str] = None,
        sid: Optional[str] = None,
        pid: Optional[int] = None,
        process: Optional[str] = None,
    ) -> None:
        super().__init__(
            name=name,
            sid=sid,
            pid=pid,
            process=process,
        )


class HashInfo(BaseModel):
    """Normalized password hash information (not available in current Volatility version)."""

    username: Optional[str] = None
    hash_value: Optional[str] = None
    hash_type: Optional[str] = None  # NTLM, LM, SHA-512, etc.
    note: Optional[str] = Field(
        default="Hash extraction not available in current Volatility 3 version"
    )

    def __init__(
        self,
        username: Optional[str] = None,
        hash_value: Optional[str] = None,
        hash_type: Optional[str] = None,
        note: Optional[str] = None,
    ) -> None:
        super().__init__(
            username=username,
            hash_value=hash_value,
            hash_type=hash_type,
            note=note or "Hash extraction not available in current Volatility 3 version",
        )


class QuickTriageOutput(BaseModel):
    """Output for quick_triage workflow."""

    processes: List[ProcessInfo] = Field(default_factory=list)
    network_connections: List[NetworkConnection] = Field(default_factory=list)
    malfind_hits: List[MalfindHit] = Field(default_factory=list)
    users: List[UserInfo] = Field(default_factory=list)
    hashes: List[HashInfo] = Field(default_factory=list)


class OutputNormalizer:
    """Normalizes plugin outputs to structured schemas."""

    def normalize_pslist(self, raw_output: List[Dict[str, Any]]) -> List[ProcessInfo]:
        """Normalize pslist output."""
        normalized: List[ProcessInfo] = []
        for item in raw_output:
            # Map Volatility 3 field names to our schema
            process = ProcessInfo(
                pid=int(item.get("PID", 0)),
                name=str(item.get("ImageFileName", "")),
                ppid=item.get("PPID"),
                threads=item.get("Threads"),
                handles=item.get("Handles"),
                session=item.get("SessionId"),
                wow64=item.get("Wow64"),
                create_time=item.get("CreateTime"),
                exit_time=item.get("ExitTime"),
            )
            normalized.append(process)
        return normalized

    def normalize_netscan(self, raw_output: List[Dict[str, Any]]) -> List[NetworkConnection]:
        """Normalize netscan output."""
        normalized: List[NetworkConnection] = []
        for item in raw_output:
            # Some outputs use "Offset(V)" instead of "Offset"
            offset_val = (
                item.get("Offset") if item.get("Offset") is not None else item.get("Offset(V)")
            )
            conn = NetworkConnection(
                offset=str(offset_val) if offset_val is not None else None,
                pid=item.get("PID"),
                owner=item.get("Owner"),
                created=item.get("Created"),
                local_addr=(
                    f"{item.get('LocalAddr')}:{item.get('LocalPort')}"
                    if item.get("LocalAddr") and item.get("LocalPort")
                    else None
                ),
                remote_addr=(
                    f"{item.get('ForeignAddr')}:{item.get('ForeignPort')}"
                    if item.get("ForeignAddr") is not None and item.get("ForeignPort") is not None
                    else None
                ),
                state=item.get("State"),
            )
            normalized.append(conn)
        return normalized

    def normalize_malfind(self, raw_output: List[Dict[str, Any]]) -> List[MalfindHit]:
        """Normalize malfind output."""
        normalized: List[MalfindHit] = []
        for item in raw_output:
            hit = MalfindHit(
                pid=item.get("PID"),
                process_name=item.get("Process"),
                start=str(item.get("Start VPN")) if item.get("Start VPN") is not None else None,
                end=str(item.get("End VPN")) if item.get("End VPN") is not None else None,
                tag=item.get("Tag"),
                protection=item.get("Protection"),
                commit_charge=item.get("CommitCharge"),
                private_memory=item.get("PrivateMemory"),
            )
            normalized.append(hit)
        return normalized

    def normalize_users(self, raw_output: List[Dict[str, Any]]) -> List[UserInfo]:
        """Normalize user information output from windows.getsids."""
        normalized: List[UserInfo] = []
        seen = set()
        for item in raw_output:
            name = item.get("Name")
            sid = item.get("SID")
            key = (name, sid)
            if key not in seen:
                seen.add(key)
                user = UserInfo(
                    name=name,
                    sid=sid,
                    pid=item.get("PID"),
                    process=item.get("Process"),
                )
                normalized.append(user)
        return normalized

    def normalize_hashes(self, raw_output: List[Dict[str, Any]]) -> List[HashInfo]:
        """Normalize password hash output (not available in current Volatility version)."""
        # Hash extraction is not available in the current Volatility 3 version
        # Return a single entry indicating this
        return [
            HashInfo(
                note=(
                    "Hash extraction plugins (hashdump, lsadump, cachedump) "
                    "are not available in this Volatility 3 version"
                )
            )
        ]

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
            elif result.plugin_name == "windows.getsids" and result.output:
                output.users = self.normalize_users(result.output)

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
            base_path = path.with_suffix("")

            # Processes
            if output.processes:
                processes_path = Path(f"{base_path}_processes.csv")
                with open(processes_path, "w", newline="", encoding="utf-8") as f:
                    if output.processes:
                        writer = csv.DictWriter(
                            f, fieldnames=output.processes[0].model_dump().keys()
                        )
                        writer.writeheader()
                        for item in output.processes:
                            writer.writerow(item.model_dump())
                logger.info(f"Exported processes to CSV: {processes_path}")

            # Network connections
            if output.network_connections:
                net_path = Path(f"{base_path}_network.csv")
                with open(net_path, "w", newline="", encoding="utf-8") as f:
                    if output.network_connections:
                        writer = csv.DictWriter(
                            f, fieldnames=output.network_connections[0].model_dump().keys()
                        )
                        writer.writeheader()
                        for item in output.network_connections:
                            writer.writerow(item.model_dump())
                logger.info(f"Exported network connections to CSV: {net_path}")

            # Malfind hits
            if output.malfind_hits:
                malfind_path = Path(f"{base_path}_malfind.csv")
                with open(malfind_path, "w", newline="", encoding="utf-8") as f:
                    if output.malfind_hits:
                        writer = csv.DictWriter(
                            f, fieldnames=output.malfind_hits[0].model_dump().keys()
                        )
                        writer.writeheader()
                        for item in output.malfind_hits:
                            writer.writerow(item.model_dump())
                logger.info(f"Exported malfind hits to CSV: {malfind_path}")

            # Users
            if output.users:
                users_path = Path(f"{base_path}_users.csv")
                with open(users_path, "w", newline="", encoding="utf-8") as f:
                    if output.users:
                        writer = csv.DictWriter(f, fieldnames=output.users[0].model_dump().keys())
                        writer.writeheader()
                        for item in output.users:
                            writer.writerow(item.model_dump())
                logger.info(f"Exported users to CSV: {users_path}")

            # Password hashes
            if output.hashes:
                hashes_path = Path(f"{base_path}_hashes.csv")
                with open(hashes_path, "w", newline="", encoding="utf-8") as f:
                    if output.hashes:
                        writer = csv.DictWriter(f, fieldnames=output.hashes[0].model_dump().keys())
                        writer.writeheader()
                        for item in output.hashes:
                            writer.writerow(item.model_dump())
                logger.info(f"Exported password hashes to CSV: {hashes_path}")
        else:
            # Generic export for other models
            with open(path, "w", newline="", encoding="utf-8") as f:
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
