import pytest
from sqlalchemy import (
    delete,
    select,
    UniqueConstraint,
)

import galaxy.model.mapping as mapping


@pytest.fixture(scope='module')
def model():
    db_uri = 'sqlite:///:memory:'
    return mapping.init('/tmp', db_uri, create_tables=True)


@pytest.fixture
def session(model):
    Session = model.session
    yield Session()
    Session.remove()  # Ensures we get a new session for each test


def test_Group_table(model):
    tbl = model.Group.__table__
    assert tbl.name == 'galaxy_group'


def test_Group(model, session):
    cls = model.Group
    name = 'a'
    obj = cls(name)
    persist(session, obj)

    stmt = select(cls)
    stored_obj = session.execute(stmt).scalar_one()
    assert stored_obj.id
    assert stored_obj.create_time
    assert stored_obj.update_time
    assert stored_obj.name == name
    assert stored_obj.deleted is False

    cleanup(session, cls)


def test_Quota_table(model):
    tbl = model.Quota.__table__
    assert tbl.name == 'quota'


def test_Quota(model, session):
    cls = model.Quota
    name, description = 'a', 'b'
    obj = cls(name, description)
    persist(session, obj)

    stmt = select(cls)
    stored_obj = session.execute(stmt).scalar_one()
    assert stored_obj.id
    assert stored_obj.create_time
    assert stored_obj.update_time
    assert stored_obj.name == name
    assert stored_obj.description == description
    assert stored_obj.bytes == 0
    assert stored_obj.operation == '='
    assert stored_obj.deleted is False

    cleanup(session, cls)


def test_Role_table(model):
    tbl = model.Role.__table__
    assert tbl.name == 'role'


def test_Role(model, session):
    cls = model.Role
    name, description = 'a', 'b'
    obj = cls(name, description)
    persist(session, obj)

    stmt = select(cls)
    stored_obj = session.execute(stmt).scalar_one()
    assert stored_obj.id
    assert stored_obj.create_time
    assert stored_obj.update_time
    assert stored_obj.name == name
    assert stored_obj.description == description
    assert stored_obj.type == model.Role.types.SYSTEM
    assert stored_obj.deleted is False

    cleanup(session, cls)


def test_WorkerProcess_table(model):
    tbl = model.WorkerProcess.__table__
    assert tbl.name == 'worker_process'
    assert has_unique_constraint(tbl, ('server_name', 'hostname'))


def test_WorkerProcess(model, session):
    cls = model.WorkerProcess
    server_name, hostname = 'a', 'b'
    obj = cls(server_name, hostname)
    persist(session, obj)

    stmt = select(cls)
    stored_obj = session.execute(stmt).scalar_one()
    assert stored_obj.id
    assert stored_obj.server_name == server_name
    assert stored_obj.hostname == hostname
    assert stored_obj.pid is None
    assert stored_obj.update_time

    cleanup(session, cls)


def test_PSAAssociation_table(model):
    tbl = model.PSAAssociation.__table__
    assert tbl.name == 'psa_association'


def test_PSAAssociation(model, session):
    cls = model.PSAAssociation
    server_url, handle, secret, issued, lifetime, assoc_type = 'a', 'b', 'c', 1, 2, 'd'
    obj = cls(server_url, handle, secret, issued, lifetime, assoc_type)
    persist(session, obj)

    stmt = select(cls)
    stored_obj = session.execute(stmt).scalar_one()
    assert stored_obj.id
    assert stored_obj.server_url == server_url
    assert stored_obj.handle == handle
    assert stored_obj.secret == secret
    assert stored_obj.issued == issued
    assert stored_obj.lifetime == lifetime
    assert stored_obj.assoc_type == assoc_type

    cleanup(session, cls)


def test_PSACode_table(model):
    tbl = model.PSACode.__table__
    assert tbl.name == 'psa_code'
    assert has_unique_constraint(tbl, ('code', 'email'))


def test_PSACode(model, session):
    cls = model.PSACode
    email, code = 'a', 'b'
    obj = cls(email, code)
    persist(session, obj)

    stmt = select(cls)
    stored_obj = session.execute(stmt).scalar_one()
    assert stored_obj.id
    assert stored_obj.email == email
    assert stored_obj.code == code

    cleanup(session, cls)


def test_PSANonce_table(model):
    tbl = model.PSANonce.__table__
    assert tbl.name == 'psa_nonce'


def test_PSANonce(model, session):
    cls = model.PSANonce
    server_url, timestamp, salt = 'a', 1, 'b'
    obj = cls(server_url, timestamp, salt)
    persist(session, obj)

    stmt = select(cls)
    stored_obj = session.execute(stmt).scalar_one()
    assert stored_obj.id
    assert stored_obj.server_url
    assert stored_obj.timestamp == timestamp
    assert stored_obj.salt == salt

    cleanup(session, cls)


def test_PSAPartial_table(model):
    tbl = model.PSAPartial.__table__
    assert tbl.name == 'psa_partial'


def test_PSAPartial(model, session):
    cls = model.PSAPartial
    token, data, next_step, backend = 'a', 'b', 1, 'c'
    obj = cls(token, data, next_step, backend)
    persist(session, obj)

    stmt = select(cls)
    stored_obj = session.execute(stmt).scalar_one()
    assert stored_obj.id
    assert stored_obj.token == token
    assert stored_obj.data == data
    assert stored_obj.next_step == next_step
    assert stored_obj.backend == backend

    cleanup(session, cls)


def persist(session, obj):
    session.add(obj)
    session.flush()


def cleanup(session, cls):
    session.execute(delete(cls))


def has_unique_constraint(table, fields):
    for constraint in table.constraints:
        if isinstance(constraint, UniqueConstraint):
            col_names = {c.name for c in constraint.columns}
            if set(fields) == col_names:
                return True
