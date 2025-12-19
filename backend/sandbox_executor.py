import os
import logging
import tempfile
import subprocess
import json
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)

class DockerSandboxExecutor:
    """
    Executes AI-generated Python code in a secure Docker sandbox
    Prevents malicious code from accessing the host system
    """
    
    def __init__(self, docker_image: str = "python:3.11-slim", timeout: int = 30):
        self.docker_image = docker_image
        self.timeout = timeout
        
    def execute_code(self, code: str, env_vars: Dict[str, str] = None) -> Tuple[bool, Dict[str, Any], str]:
        """
        Execute Python code in Docker sandbox
        
        Args:
            code: Python code to execute
            env_vars: Environment variables to pass to the sandbox
        
        Returns:
            Tuple of (success, result_dict, error_message)
        """
        logger.info("Starting code execution in Docker sandbox")
        
        # Create temporary directory for code execution
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write code to temporary file
            code_file = os.path.join(tmpdir, "script.py")
            with open(code_file, 'w') as f:
                f.write(code)
            
            # Write result to file
            result_file = os.path.join(tmpdir, "result.json")
            
            # Modify code to save result to file
            modified_code = code + "\n\n"
            modified_code += f"""
import json
try:
    with open('{result_file}', 'w') as f:
        json.dump(result, f)
except Exception as e:
    with open('{result_file}', 'w') as f:
        json.dump({{'error': str(e)}}, f)
"""
            
            with open(code_file, 'w') as f:
                f.write(modified_code)
            
            # Build docker run command
            env_args = []
            if env_vars:
                for key, value in env_vars.items():
                    env_args.extend(['-e', f'{key}={value}'])
            
            docker_cmd = [
                'docker', 'run',
                '--rm',  # Remove container after execution
                '--network', 'host',  # Allow network access for API calls
                '--memory', '512m',  # Limit memory
                '--cpus', '1.0',  # Limit CPU
                *env_args,  # Environment variables
                '-v', f'{tmpdir}:/workspace',  # Mount temporary directory
                '-w', '/workspace',  # Set working directory
                self.docker_image,
                'python', 'script.py'
            ]
            
            try:
                # Execute code in Docker
                logger.info(f"Executing Docker command: {' '.join(docker_cmd[:8])}...")
                result = subprocess.run(
                    docker_cmd,
                    timeout=self.timeout,
                    capture_output=True,
                    text=True
                )
                
                # Check if execution was successful
                if result.returncode != 0:
                    error_msg = f"Docker execution failed: {result.stderr}"
                    logger.error(error_msg)
                    return False, {}, error_msg
                
                # Read result from file
                if os.path.exists(result_file):
                    with open(result_file, 'r') as f:
                        result_data = json.load(f)
                    
                    if 'error' in result_data:
                        logger.error(f"Code execution error: {result_data['error']}")
                        return False, result_data, result_data['error']
                    
                    logger.info("Code executed successfully in Docker sandbox")
                    return True, result_data, ""
                else:
                    error_msg = "Result file not created"
                    logger.error(error_msg)
                    return False, {}, error_msg
                    
            except subprocess.TimeoutExpired:
                error_msg = f"Code execution timed out after {self.timeout} seconds"
                logger.error(error_msg)
                return False, {}, error_msg
            except Exception as e:
                error_msg = f"Docker execution exception: {str(e)}"
                logger.error(error_msg)
                return False, {}, error_msg

class SimpleSandboxExecutor:
    """
    Fallback executor without Docker (for development/testing)
    WARNING: Less secure than Docker sandbox
    """
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        
    def execute_code(self, code: str, env_vars: Dict[str, str] = None) -> Tuple[bool, Dict[str, Any], str]:
        """
        Execute Python code using exec() with restricted environment
        
        Args:
            code: Python code to execute
            env_vars: Environment variables to set
        
        Returns:
            Tuple of (success, result_dict, error_message)
        """
        logger.info("Starting code execution in simple sandbox (NO DOCKER)")
        
        # Set environment variables
        if env_vars:
            for key, value in env_vars.items():
                os.environ[key] = value
        
        # Create restricted namespace
        namespace = {
            '__builtins__': __builtins__,
            'os': os,
            'json': json,
            'requests': None,  # Will be imported by the code if needed
        }
        
        try:
            # Import requests for the namespace
            import requests
            namespace['requests'] = requests
            
            # Execute code
            exec(code, namespace)
            
            # Get result
            if 'result' in namespace:
                result = namespace['result']
                if isinstance(result, dict) and 'error' in result:
                    logger.error(f"Code execution error: {result['error']}")
                    return False, result, result['error']
                
                logger.info("Code executed successfully")
                return True, result, ""
            else:
                error_msg = "Code did not produce a 'result' variable"
                logger.error(error_msg)
                return False, {}, error_msg
                
        except Exception as e:
            error_msg = f"Code execution exception: {str(e)}"
            logger.error(error_msg)
            return False, {}, error_msg

def get_sandbox_executor(use_docker: bool = True) -> Any:
    """Factory function to get appropriate sandbox executor"""
    if use_docker:
        # Check if Docker is available
        try:
            result = subprocess.run(['docker', '--version'], capture_output=True, timeout=5)
            if result.returncode == 0:
                logger.info("Docker is available, using DockerSandboxExecutor")
                return DockerSandboxExecutor()
        except Exception as e:
            logger.warning(f"Docker not available: {e}")
    
    logger.info("Using SimpleSandboxExecutor (fallback)")
    return SimpleSandboxExecutor()
