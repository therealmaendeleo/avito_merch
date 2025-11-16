from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import BasePgInterface, with_session, with_session_commit
from app.database.models import Employee


class EmployeeRepo(BasePgInterface):
    """Репозиторий для работы с сотрудниками."""

    @with_session
    async def get(
        self,
        username: str,
        session: AsyncSession | None = None,
    ) -> Employee | None:
        query = select(Employee).where(Employee.name == username)
        result = await session.execute(query)  # type: ignore
        return result.scalar_one_or_none()

    @with_session_commit
    async def create(
        self,
        username: str,
        hashed_password: str,
        balance: int = 1000,
        session: AsyncSession | None = None,
    ) -> Employee:
        employee = Employee(
            name=username,
            hashed_password=hashed_password,
            balance=balance,
        )
        session.add(employee)  # type: ignore
        await session.flush()  # type: ignore
        await session.refresh(employee)  # type: ignore
        return employee


employee_repo = EmployeeRepo()
