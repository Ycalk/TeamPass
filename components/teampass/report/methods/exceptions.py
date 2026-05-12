from uuid import UUID

from teampass.domain_core import DomainNotFoundException


class ReportNotFoundException(DomainNotFoundException):
    def __init__(self, report_id: UUID) -> None:
        self.report_id: UUID = report_id
        super().__init__(f"Report with ID {report_id} not found")
