#!/bin/bash
ROBOTS_FILE="https://raw.githubusercontent.com/ai-robots-txt/ai.robots.txt/refs/heads/main/robots.json"
curl -s $ROBOTS_FILE | jq 'keys' | cat <(echo -n "AGENTS = ") - > src/django_llm_poison/agents.py
