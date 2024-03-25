import sqlalchemy as sa

class User(Base, UserMixin):
    password = sa.Column(sa.String(256), nullable=False)

