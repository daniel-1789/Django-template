# Use PyMySQL as the MySQL driver so the template stays pure-Python (no C build
# toolchain, matching the SQLite-by-default story). This shim makes PyMySQL
# masquerade as mysqlclient, which is what Django's mysql backend imports. It's
# a no-op for the SQLite backend, so it's safe to run unconditionally here —
# this module is imported once, before Django touches the database.
try:
    import pymysql

    pymysql.install_as_MySQLdb()
except ModuleNotFoundError:
    # PyMySQL isn't installed (e.g. SQLite-only environments). Fine — Django only
    # needs it when DATABASE_URL points at MySQL.
    pass
