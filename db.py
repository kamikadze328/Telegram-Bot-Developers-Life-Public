import os

import ydb

import Image

driver = ydb.Driver(endpoint=os.getenv('YDB_ENDPOINT'), database=os.getenv('YDB_DATABASE'))
driver.wait(fail_fast=True, timeout=5)
pool = ydb.SessionPool(driver)


def execute(query: str, my_dict: dict = {}):
    def callee(session):
        prepared_query = session.prepare(query)
        return session.transaction().execute(prepared_query, my_dict, commit_tx=True)

    return pool.retry_operation_sync(callee)


def get_all_images():
    return execute("SELECT * FROM Image;")[0].rows


def save_request(request: str, username: str) -> int:
    id = get_last_result_id() + 1
    query = """
        DECLARE $request AS Utf8;
        DECLARE $telegram_username AS Utf8;
    
        INSERT INTO UserRequest(id, request, telegram_username) VALUES({}, $request, $telegram_username)""".format(id)

    execute(query, {
        '$request': request.encode('utf-8'),
        '$telegram_username': username.encode('utf-8'),
    })
    return id


def save_result(request_id: int, result: Image.Image):
    query = """
        DECLARE $image_id AS Utf8;
    
        INSERT INTO Result(user_request_id, image_id, user_rating) VALUES({}, $image_id, NULL)""".format(request_id)

    return execute(query, {
        '$image_id': result.filename.encode('utf-8'),
    })


def get_last_result_id() -> int:
    query = "SELECT IF(max(id) IS NULL, 0, max(id)) AS id FROM UserRequest;"
    return int(execute(query)[0].rows[0].id)


def get_last_result_id_by_username(username: str) -> int:
    query = """
        DECLARE $telegram_username AS Utf8;
        SELECT IF(max(id) IS NULL, -1, max(id)) AS id FROM UserRequest WHERE telegram_username=$telegram_username;"""
    result = execute(query, {
        '$telegram_username': username.encode('utf-8'),
    })
    return int(result[0].rows[0].id)


def save_rating(username: str, rating: int):
    id = get_last_result_id_by_username(username)
    if id == -1:
        return False

    query = """
        UPDATE Result
            SET user_rating = {}
            WHERE user_request_id = {};
        """.format(rating, id)
    execute(query)
    return True


def get_local_image_path(service_id: int) -> str:
    query = "SELECT local_url FROM Service WHERE id={};".format(service_id)
    result = execute(query)
    return result[0].rows[0].local_url
