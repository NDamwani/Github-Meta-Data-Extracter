from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from tree_sitter import Language, Parser
import tree_sitter_python as tspython
import os
import shutil
from git import Repo

from database import get_db
from models import Function
from schemas import RepoOperationSchema
from oauth2 import get_current_user
import logging


router = APIRouter(tags=['Github Operations'])

PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)


@router.post("/operate-repo")
async def operate_repo(repo_data: RepoOperationSchema, db: Session = Depends(get_db), user_id:int = Depends(get_current_user)):
    print("Starting repo operation for: %s", repo_data.repo_url)
    repo_url = repo_data.repo_url
    temp_dir = "temp_repo"
    # pr = None
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    try:
        repo = Repo.clone_from(repo_url, temp_dir)
        print("Repo cloned successfully")
        for root, dirs, files in os.walk(temp_dir):
            print("Walking in directory: %s", root)
            for file in files:
                print("Checking file: %s", file)
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    print("Processing Python file: %s", file_path)
                    with open(file_path, 'r') as f:
                        # print("inside operate repo")
                        code = f.read()
                        tree = parser.parse(bytes(code, 'utf8'))
                        functions = parse_functions(tree, code, file_path)
                        # pr = function
                        store_functions_in_db(db, file, functions)
                        print("Stored functions from file: %s", file_path)
        return {"message": "Repository processed"}
    finally:
        shutil.rmtree(temp_dir)
        print("Cleaned up temporary directory")

def parse_functions(tree, code, file_path):
    print("inside parse function")
    root_node = tree.root_node
    functions = []
    for node in root_node.children:
        if node.type == 'function_definition':
            function_name = node.child_by_field_name('name').text.decode('utf8')
            start_byte, end_byte = node.start_byte, node.end_byte
            function_code = code[start_byte:end_byte]
            class_node = node.parent if node.parent.type == 'class_definition' else None
            class_name = class_node.child_by_field_name('name').text.decode('utf8') if class_node else None
            functions.append({
                'file_name': os.path.basename(file_path),
                'function_name': function_name,
                'class_name': class_name,
                'code': function_code
            })
            print("this is functions", functions)
    return functions

def store_functions_in_db(db, file_name, functions):
    try:
        for function in functions:
            new_function = Function(**function)
            db.add(new_function)
        db.commit()
        print("Database commit successful for file: %s", file_name)
    except Exception as e:
        db.rollback()
        logging.error("Failed to commit functions to database: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

