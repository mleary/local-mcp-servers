import os
import json
import tempfile
from pathlib import Path
from kroger_api import KrogerAPI

class MCPKrogerAPI:
    def __init__(self):
        # Create a temp directory for tokens
        self.token_dir = Path(tempfile.gettempdir()) / "kroger-mcp-tokens"
        self.token_dir.mkdir(exist_ok=True)
        
        # Store tokens in memory as fallback
        self.tokens = {}
        
        # Monkey-patch the token storage functions
        self._patch_token_storage()
        
        # Initialize the actual API
        self.api = KrogerAPI()
    
    def _patch_token_storage(self):
        import kroger_api.token_storage as token_storage
        
        # Override save_token function
        original_save = token_storage.save_token
        def save_token_wrapper(token_info, token_file):
            try:
                # Try to save to temp directory
                temp_path = self.token_dir / Path(token_file).name
                with open(temp_path, 'w') as f:
                    json.dump(token_info, f)
                # Also store in memory
                self.tokens[token_file] = token_info
            except Exception as e:
                # Fall back to memory-only storage
                self.tokens[token_file] = token_info
        
        token_storage.save_token = save_token_wrapper
        
        # Override load_token function  
        original_load = token_storage.load_token
        def load_token_wrapper(token_file):
            path_obj = Path(token_file).expanduser()

            # 1) Respect explicit absolute paths (e.g., when provided via env var or resolved in server)
            try:
                if path_obj.is_absolute() and path_obj.exists():
                    with open(path_obj, 'r') as f:
                        return json.load(f)
            except Exception:
                pass

            try:
                # Try to load from temp directory first
                temp_path = self.token_dir / path_obj.name
                if temp_path.exists():
                    with open(temp_path, 'r') as f:
                        return json.load(f)
            except:
                pass
            
            # Fall back to memory storage
            if token_file in self.tokens:
                return self.tokens[token_file]

            # 4) Last chance: original loader (covers relative paths in cwd)
            try:
                return original_load(token_file)
            except Exception:
                pass
            
            # Return None if not found
            return None
        
        token_storage.load_token = load_token_wrapper