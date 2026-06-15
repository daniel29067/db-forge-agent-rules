#!/usr/bin/env python3
import os
import sys
import re
import argparse
from typing import List, Tuple

# ANSI color codes for execution output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

class SchemaAuditor:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.violations: List[Tuple[str, str, int, str]] = []  # (file_path, type, line_no, message)

    def log_violation(self, file_path: str, v_type: str, line_no: int, message: str):
        self.violations.append((file_path, v_type, line_no, message))

    def audit_sql_file(self, file_path: str, content: str):
        lines = content.splitlines()
        
        # Check for procedural loops/cursors globally in the file
        for idx, line in enumerate(lines, start=1):
            cleaned = line.upper().strip()
            # Ignore comments
            if cleaned.startswith("--") or cleaned.startswith("/*"):
                continue
            
            if "DECLARE" in cleaned and "CURSOR" in cleaned:
                self.log_violation(file_path, "PROCEDURAL_ANTI_PATTERN", idx, "Detected SQL Cursor declaration. Prefer set-based operations.")
            if re.search(r"\bWHILE\b", cleaned) and not re.search(r"\bEND\s+WHILE\b", cleaned):
                # Basic warning on WHILE loops in SQL
                self.log_violation(file_path, "PROCEDURAL_ANTI_PATTERN", idx, "Detected WHILE loop statement. Prefer set-based updates/inserts.")

        # Find CREATE TABLE blocks and verify audit columns
        # Capture from CREATE TABLE (with optional IF NOT EXISTS and optional quotes/placeholders) until matching );
        matches = re.finditer(
            r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:[\"']?([\w{}]+)[\"']?)\s*\((.*?)\);",
            content,
            re.IGNORECASE | re.DOTALL
        )
        for match in matches:
            table_name = match.group(1)
            table_body = match.group(2)
            
            # Find the line number of CREATE TABLE
            start_pos = match.start()
            line_no = content[:start_pos].count("\n") + 1
            
            body_upper = table_body.upper()
            
            # Check for audit columns
            has_created_at = "CREATED_AT" in body_upper or "CREATEDAT" in body_upper
            has_updated_at = "UPDATED_AT" in body_upper or "UPDATEDAT" in body_upper
            has_deleted_or_active = any(col in body_upper for col in ["DELETED_AT", "DELETEDAT", "IS_ACTIVE", "ISACTIVE"])
            
            missing = []
            if not has_created_at:
                missing.append("created_at")
            if not has_updated_at:
                missing.append("updated_at")
            if not has_deleted_or_active:
                missing.append("is_active or deleted_at")
                
            if missing:
                self.log_violation(
                    file_path,
                    "MISSING_AUDIT_COLUMNS",
                    line_no,
                    f"Table '{table_name}' is missing audit fields: {', '.join(missing)}"
                )

    def audit_prisma_file(self, file_path: str, content: str):
        lines = content.splitlines()
        
        # Find all model blocks
        # e.g., model User { ... }
        model_matches = re.finditer(r"model\s+(\w+)\s*\{(.*?)\}", content, re.DOTALL)
        models_fields = {} # model_name -> list of (field_name, field_type)
        
        for match in model_matches:
            model_name = match.group(1)
            body = match.group(2)
            
            start_pos = match.start()
            line_no = content[:start_pos].count("\n") + 1
            
            # Extract fields
            fields = []
            body_lines = body.splitlines()
            for bl in body_lines:
                bl = bl.strip()
                if not bl or bl.startswith("//") or bl.startswith("@@"):
                    continue
                parts = bl.split()
                if len(parts) >= 2:
                    field_name = parts[0]
                    field_type = parts[1]
                    fields.append((field_name, field_type))
            
            models_fields[model_name] = fields
            
            # Check for audit columns in Prisma
            field_names = [f[0].lower() for f in fields]
            has_created_at = "createdat" in field_names or "created_at" in field_names
            has_updated_at = "updatedat" in field_names or "updated_at" in field_names
            has_deleted_or_active = any(f in field_names for f in ["isactive", "is_active", "deletedat", "deleted_at"])
            
            missing = []
            if not has_created_at:
                missing.append("createdAt")
            if not has_updated_at:
                missing.append("updatedAt")
            if not has_deleted_or_active:
                missing.append("isActive or deletedAt")
                
            if missing:
                self.log_violation(
                    file_path,
                    "MISSING_AUDIT_COLUMNS",
                    line_no,
                    f"Prisma model '{model_name}' is missing audit fields: {', '.join(missing)}"
                )

        # Detect Implicit Many-to-Many Relationships
        # Check if Model A references Model B[] and Model B references Model A[] directly
        for model_name, fields in models_fields.items():
            for field_name, field_type in fields:
                if field_type.endswith("[]"):
                    target_model = field_type[:-2]
                    # Check if target model has a relation array pointing back to this model
                    if target_model in models_fields:
                        target_fields = models_fields[target_model]
                        for tf_name, tf_type in target_fields:
                            if tf_type == f"{model_name}[]":
                                # This is an implicit M:N relation
                                # Find line number of the field
                                line_index = 0
                                for idx, line in enumerate(lines, start=1):
                                    if field_name in line and field_type in line:
                                        line_index = idx
                                        break
                                self.log_violation(
                                    file_path,
                                    "IMPLICIT_MANY_TO_MANY",
                                    line_index,
                                    f"Detected implicit Many-to-Many relation between '{model_name}' and '{target_model}' on field '{field_name}'. Enforce explicit junction model."
                                )

    def audit_sqlalchemy_file(self, file_path: str, content: str):
        lines = content.splitlines()
        
        # Check for classes inheriting from Base
        # We can look for class declarations: class MyModel(Base, AuditMixin): or similar
        class_matches = re.finditer(r"class\s+(\w+)\s*\((.*?)\)\s*:", content)
        for match in class_matches:
            class_name = match.group(1)
            inheritance = match.group(2)
            
            start_pos = match.start()
            line_no = content[:start_pos].count("\n") + 1
            
            # If it inherits from Base, it should inherit from AuditMixin
            bases = [b.strip() for b in inheritance.split(",")]
            if "Base" in bases:
                if "AuditMixin" not in bases:
                    # Let's check if the class declares its own audit columns locally
                    class_body_start = match.end()
                    # Look ahead for class body until the next class or end of file
                    next_class = re.search(r"class\s+", content[class_body_start:])
                    class_body = content[class_body_start:class_body_start + next_class.start()] if next_class else content[class_body_start:]
                    
                    body_upper = class_body.upper()
                    has_created_at = "CREATED_AT" in body_upper
                    has_updated_at = "UPDATED_AT" in body_upper
                    has_deleted_or_active = any(col in body_upper for col in ["DELETED_AT", "IS_ACTIVE"])
                    
                    if not (has_created_at and has_updated_at and has_deleted_or_active):
                        self.log_violation(
                            file_path,
                            "MISSING_AUDIT_MIXIN",
                            line_no,
                            f"SQLAlchemy model '{class_name}' should inherit from 'AuditMixin' or define standard audit columns."
                        )

    def audit_file(self, file_path: str):
        if not os.path.exists(file_path):
            print(f"{RED}File not found: {file_path}{RESET}")
            return
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"{RED}Error reading {file_path}: {e}{RESET}")
            return

        if file_path.endswith(".sql"):
            self.audit_sql_file(file_path, content)
        elif file_path.endswith(".prisma"):
            self.audit_prisma_file(file_path, content)
        elif file_path.endswith(".py"):
            self.audit_sqlalchemy_file(file_path, content)

    def scan_directory(self, dir_path: str):
        for root, _, files in os.walk(dir_path):
            # Skip hidden folders (.git, .gemini, etc.)
            if any(part.startswith(".") for part in root.split(os.sep)):
                continue
            for file in files:
                ext = os.path.splitext(file)[1]
                if ext in [".sql", ".prisma", ".py"]:
                    # Skip audit_schema.py itself
                    if file == "audit_schema.py":
                        continue
                    full_path = os.path.join(root, file)
                    self.audit_file(full_path)

    def report(self) -> int:
        if not self.violations:
            print(f"\n{GREEN}[PASS] All schema files passed database architect audits!{RESET}")
            return 0
        
        print(f"\n{RED}[FAIL] Found {len(self.violations)} database architecture violations:{RESET}\n")
        current_file = ""
        for file_path, v_type, line_no, msg in sorted(self.violations):
            if file_path != current_file:
                print(f"{BLUE}[File: {file_path}]{RESET}")
                current_file = file_path
            print(f"  {YELLOW}Line {line_no}{RESET} | [{v_type}] {msg}")
            
        return 1

def main():
    parser = argparse.ArgumentParser(description="Audit database DDL, Prisma schemas, and SQLAlchemy ORM models.")
    parser.add_argument("path", nargs="?", default=".", help="Path to a file or directory to scan.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose logging.")
    args = parser.parse_args()

    auditor = SchemaAuditor(verbose=args.verbose)
    
    if os.path.isdir(args.path):
        auditor.scan_directory(args.path)
    else:
        auditor.audit_file(args.path)
        
    sys.exit(auditor.report())

if __name__ == "__main__":
    main()
