#!/bin/bash
source venv/bin/activate
uvicorn backend.main:app --reload

