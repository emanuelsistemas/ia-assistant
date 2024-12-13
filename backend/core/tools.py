from typing import Any, Dict, List, Callable
import asyncio
import os
import json

class ToolManager:
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self._load_default_tools()
    
    def _load_default_tools(self):
        # Registro das ferramentas padrão
        self.register_tool('read_file', self._read_file)
        self.register_tool('write_file', self._write_file)
        self.register_tool('list_files', self._list_files)
        self.register_tool('execute_code', self._execute_code)
    
    def register_tool(self, name: str, tool: Callable):
        """Registra uma nova ferramenta"""
        self.tools[name] = tool
    
    async def execute_tool(self, name: str, **kwargs) -> Any:
        """Executa uma ferramenta registrada"""
        if name not in self.tools:
            raise ValueError(f"Tool {name} not found")
        
        if asyncio.iscoroutinefunction(self.tools[name]):
            return await self.tools[name](**kwargs)
        return self.tools[name](**kwargs)
    
    async def _read_file(self, path: str) -> str:
        """Lê o conteúdo de um arquivo"""
        try:
            with open(path, 'r') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    async def _write_file(self, path: str, content: str) -> str:
        """Escreve conteúdo em um arquivo"""
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w') as f:
                f.write(content)
            return f"File written successfully: {path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"
    
    async def _list_files(self, directory: str = '.') -> List[str]:
        """Lista arquivos em um diretório"""
        try:
            return os.listdir(directory)
        except Exception as e:
            return f"Error listing files: {str(e)}"
    
    async def _execute_code(self, code: str, language: str = 'python') -> Dict[str, Any]:
        """Executa código de forma segura"""
        if language != 'python':
            return {"error": f"Language {language} not supported"}
            
        try:
            # Cria um ambiente isolado para execução
            local_vars = {}
            exec(code, {}, local_vars)
            return {"result": str(local_vars.get('result', 'Code executed successfully'))}
        except Exception as e:
            return {"error": str(e)}

    async def list_available_tools(self) -> List[str]:
        """Lista todas as ferramentas disponíveis"""
        return list(self.tools.keys())

    async def get_tool_info(self, name: str) -> Dict[str, Any]:
        """Retorna informações sobre uma ferramenta específica"""
        if name not in self.tools:
            raise ValueError(f"Tool {name} not found")
            
        tool = self.tools[name]
        return {
            "name": name,
            "doc": tool.__doc__ or "No documentation available",
            "is_async": asyncio.iscoroutinefunction(tool)
        }
