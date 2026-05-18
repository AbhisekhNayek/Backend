import os
import re

pattern = re.compile(r'([ \t]*)except Exception as e:\s+raise HTTPException\(status_code=500, detail=str\(e\)\)\s*', re.MULTILINE)

def repl(m):
    indent = m.group(1)
    return (
        f"{indent}except HTTPException:\n"
        f"{indent}    raise\n"
        f"{indent}except Exception as e:\n"
        f"{indent}    from app.logger import logger\n"
        f"{indent}    logger.error(f'Unhandled error: {{str(e)}}', exc_info=True)\n"
        f"{indent}    raise HTTPException(status_code=500, detail='Internal Server Error')\n\n"
    )

for root, _, files in os.walk('app'):
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            new_content = pattern.sub(repl, content)
            
            if new_content != content:
                with open(path, 'w', encoding='utf-8') as file:
                    file.write(new_content)
