import json
import os

def generate_markdown():
    with open("openapi.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    md = []
    md.append("# Docton Backend API Documentation\n")
    md.append("Welcome to the complete production API specifications for the Docton backend. This document covers the comprehensive REST API endpoints, schemas, authentication scopes, and real-time live map details.\n")
    
    paths = data.get("paths", {})
    components = data.get("components", {})
    schemas = components.get("schemas", {})
    
    def resolve_schema(schema_ref):
        if not schema_ref:
            return {}
        if "$ref" in schema_ref:
            ref_name = schema_ref["$ref"].split("/")[-1]
            return schemas.get(ref_name, {})
        return schema_ref

    def format_property_type(prop):
        p_type = prop.get("type", "any")
        if "anyOf" in prop:
            sub_types = [format_property_type(sub) for sub in prop["anyOf"] if sub.get("type") != "null"]
            return " | ".join(sub_types)
        if "enum" in prop:
            return f"enum ({', '.join([repr(e) for e in prop['enum']])})"
        if p_type == "array":
            items = prop.get("items", {})
            return f"array of {format_property_type(items)}"
        return p_type

    def build_mock_body(schema):
        resolved = resolve_schema(schema)
        p_type = resolved.get("type", "object")
        if p_type == "object":
            obj = {}
            for k, prop in resolved.get("properties", {}).items():
                res_prop = resolve_schema(prop)
                p_t = res_prop.get("type")
                if p_t == "string":
                    if "format" in res_prop and res_prop["format"] == "date-time":
                        obj[k] = "2026-05-18T23:15:00Z"
                    elif "email" in k:
                        obj[k] = "user@docton.com"
                    else:
                        obj[k] = "string"
                elif p_t == "number" or p_t == "integer":
                    obj[k] = 0 if p_t == "integer" else 0.0
                elif p_t == "boolean":
                    obj[k] = True
                elif p_t == "array":
                    items_schema = res_prop.get("items", {})
                    obj[k] = [build_mock_body(items_schema)]
                elif "$ref" in prop:
                    obj[k] = build_mock_body(prop)
                else:
                    obj[k] = {}
            return obj
        return "any"

    # Group by tags
    endpoints_by_tag = {}
    for path, methods in paths.items():
        for method, info in methods.items():
            tags = info.get("tags", ["General"])
            for tag in tags:
                if tag not in endpoints_by_tag:
                    endpoints_by_tag[tag] = []
                endpoints_by_tag[tag].append((path, method, info))

    for tag, endpoints in sorted(endpoints_by_tag.items()):
        md.append(f"## 🏷️ {tag}\n")
        
        for path, method, info in sorted(endpoints, key=lambda x: x[0]):
            summary = info.get("summary", "No summary")
            description = info.get("description", "")
            method_upper = method.upper()
            
            md.append(f"### `{method_upper}` {path}")
            md.append(f"**Description**: {summary}. {description}\n")
            
            # Parameters
            params = info.get("parameters", [])
            if params:
                md.append("#### Query/Path Parameters:")
                md.append("| Name | In | Type | Required | Description |")
                md.append("| :--- | :--- | :--- | :--- | :--- |")
                for p in params:
                    p_name = p.get("name")
                    p_in = p.get("in")
                    p_req = "Yes" if p.get("required") else "No"
                    p_schema = resolve_schema(p.get("schema", {}))
                    p_type = format_property_type(p_schema)
                    p_desc = p.get("description", "")
                    md.append(f"| `{p_name}` | {p_in} | `{p_type}` | {p_req} | {p_desc} |")
                md.append("")

            # Request Body
            req_body = info.get("requestBody")
            if req_body:
                content = req_body.get("content", {})
                json_content = content.get("application/json", {}) or content.get("multipart/form-data", {})
                schema = json_content.get("schema")
                if schema:
                    mock_json = build_mock_body(schema)
                    md.append("#### Request Body:")
                    md.append("```json")
                    md.append(json.dumps(mock_json, indent=2))
                    md.append("```\n")
            
            # Response
            responses = info.get("responses", {})
            success_res = responses.get("200") or responses.get("201")
            if success_res:
                s_content = success_res.get("content", {})
                s_json = s_content.get("application/json", {})
                s_schema = s_json.get("schema")
                if s_schema:
                    mock_resp = build_mock_body(s_schema)
                    md.append("#### Success Response (200/201):")
                    md.append("```json")
                    md.append(json.dumps(mock_resp, indent=2))
                    md.append("```\n")
            
            md.append("---\n")

    out_path = "api_documentation.md"
    
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
        
    print(f"SUCCESSFULLY WRITTEN FORMATTED API DOC TO {out_path}")

if __name__ == "__main__":
    generate_markdown()
