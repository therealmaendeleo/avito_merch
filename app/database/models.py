from datetime import datetime

from sqlalchemy import TIMESTAMP, BigInteger, CheckConstraint, ForeignKey, Integer, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Employee(Base):
    """Модель сотрудника."""

    __tablename__ = 'employees'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment='Имя сотрудника')
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False, comment='Хешированный пароль')
    balance: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1000, server_default='1000', comment='Баланс монет'
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now(), comment='Дата создания'
    )

    # Связи
    sent_transactions: Mapped[list['Transaction']] = relationship(
        'Transaction', foreign_keys='Transaction.sender_id', back_populates='sender'
    )
    received_transactions: Mapped[list['Transaction']] = relationship(
        'Transaction', foreign_keys='Transaction.receiver_id', back_populates='receiver'
    )
    purchases: Mapped[list['Purchase']] = relationship('Purchase', back_populates='employee')

    __table_args__ = (CheckConstraint('balance >= 0', name='check_balance_non_negative'),)


class Merch(Base):
    """Модель товара мерча."""

    __tablename__ = 'merch'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, comment='Название товара')
    price: Mapped[int] = mapped_column(Integer, nullable=False, comment='Цена в монетах')
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now(), comment='Дата создания'
    )

    # Связи
    purchases: Mapped[list['Purchase']] = relationship('Purchase', back_populates='merch')

    __table_args__ = (CheckConstraint('price > 0', name='check_price_positive'),)


class Transaction(Base):
    """Модель транзакции монет между сотрудниками."""

    __tablename__ = 'transactions'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    sender_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey('employees.id', ondelete='CASCADE'), nullable=False, comment='ID отправителя'
    )
    receiver_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey('employees.id', ondelete='CASCADE'), nullable=False, comment='ID получателя'
    )
    amount: Mapped[int] = mapped_column(Integer, nullable=False, comment='Количество монет')
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now(), comment='Дата транзакции'
    )

    # Связи
    sender: Mapped['Employee'] = relationship('Employee', foreign_keys=[sender_id], back_populates='sent_transactions')
    receiver: Mapped['Employee'] = relationship(
        'Employee', foreign_keys=[receiver_id], back_populates='received_transactions'
    )

    __table_args__ = (CheckConstraint('amount > 0', name='check_amount_positive'),)


class Purchase(Base):
    """Модель покупки мерча."""

    __tablename__ = 'purchases'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey('employees.id', ondelete='CASCADE'), nullable=False, comment='ID сотрудника'
    )
    merch_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey('merch.id', ondelete='RESTRICT'), nullable=False, comment='ID товара'
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1, comment='Количество')
    total_price: Mapped[int] = mapped_column(Integer, nullable=False, comment='Общая стоимость')
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now(), comment='Дата покупки'
    )

    # Связи
    employee: Mapped['Employee'] = relationship('Employee', back_populates='purchases')
    merch: Mapped['Merch'] = relationship('Merch', back_populates='purchases')

    __table_args__ = (CheckConstraint('quantity > 0', name='check_quantity_positive'),)
