# -*- coding: utf-8 -*-

import pytest
import os

# from unittest.mock import Mock
from cro.respondent.resolve.server import create_app


def test_that_server_starts():
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """

    client = create_app()

    with client.test_client() as test_client:
        response = test_client.get("/")
        assert response.status_code == 200
