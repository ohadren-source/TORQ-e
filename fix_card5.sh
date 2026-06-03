#!/bin/bash

# Fix explore_claims_data
sed -i '/if tool_name == "explore_claims_data":/,/return _prepare_tool_result_for_claude/ {
  s/db=None$/db=None,\n                    public_data_schema=public_data_schema,\n                    query_context=query_context/
}' chat.py

# Fix compute_outlier_scores
sed -i '/elif tool_name == "compute_outlier_scores":/,/return _prepare_tool_result_for_claude/ {
  s/db=None$/db=None,\n                    public_data_schema=public_data_schema,\n                    query_context=query_context/
}' chat.py

# Fix navigate_relationship_graph
sed -i '/elif tool_name == "navigate_relationship_graph":/,/return _prepare_tool_result_for_claude/ {
  s/db=None$/db=None,\n                    public_data_schema=public_data_schema,\n                    query_context=query_context/
}' chat.py

# Fix create_investigation_project
sed -i '/elif tool_name == "create_investigation_project":/,/return _prepare_tool_result_for_claude/ {
  s/db=None$/db=None,\n                    public_data_schema=public_data_schema,\n                    query_context=query_context/
}' chat.py

# Fix request_data_correction
sed -i '/elif tool_name == "request_data_correction":/,/return _prepare_tool_result_for_claude/ {
  s/db=None$/db=None,\n                    public_data_schema=public_data_schema,\n                    query_context=query_context/
}' chat.py

echo "✓ Fixed all Card 5 tool calls"
