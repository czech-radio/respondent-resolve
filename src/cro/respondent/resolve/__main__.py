#!/usr/bin/env python
# coding: utf-8

# from cro.respondent.resolve import respondent

from api import Server
import pandas as pd


def main():
    """
    The main application function.
    """

    server = Server()
    server.run()

if __name__ == "__main__":
    main()
