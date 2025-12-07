#!/usr/bin/env python
import os, sys
if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chat_project.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as e:
        raise
    execute_from_command_line(sys.argv)
