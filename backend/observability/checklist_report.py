"""
Checklist Report Generator

Generates human-readable debug/checklist reports for each NIRO request.
These reports are stored as HTML files and made available via /api/debug/checklist/{request_id}

Purpose:
- Capture full request context and processing pipeline
- Make debugging/auditing transparent to users (via "Invite alia to see this report")
- Serve as structured metadata for observability
- Help identify missing data, API issues, LLM quality issues
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import asdict

logger = logging.getLogger(__name__)


def make_request_id() -> str:
    """Generate unique request ID (import from pipeline_logger if exists)"""
    import uuid
    return str(uuid.uuid4())[:8]


class ChecklistReport:
    """Generates and stores checklist HTML reports"""
    
    def __init__(self, repo_root: Path = None):
        # Use workspace-local logs/checklists directory
        if repo_root is None:
            repo_root = Path(__file__).resolve().parents[2]
        
        self.checklists_dir = repo_root / "logs" / "checklists"
        self.checklists_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"ChecklistReport initialized at {self.checklists_dir}")
    
    def generate_report(
        self,
        request_id: str,
        session_id: str,
        user_input: str,
        birth_details: Optional[Dict] = None,
        intent_data: Optional[Dict] = None,
        time_context: Optional[Dict] = None,
        api_calls: Optional[List[Dict]] = None,
        reading_pack: Optional[Dict] = None,
        llm_metadata: Optional[Dict] = None,
        llm_response: Optional[Dict] = None,
        errors: Optional[List[str]] = None,
        final_response: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive checklist report HTML.
        
        Args:
        - request_id: Unique request identifier
        - session_id: User session identifier  
        - user_input: Raw user message
        - birth_details: Parsed birth details {dob, tob, location, lat, lon, tz}
        - intent_data: Intent classification {topic, mode, action_id}
        - time_context: Time context inference {current_date, timeframe, relevant_dates}
        - api_calls: List of API calls made {endpoint, status, duration, error}
        - reading_pack: Astro signals {kept_count, dropped_count, top_signals[]}
        - llm_metadata: LLM call info {model, tokens_prompt, tokens_completion, temperature}
        - llm_response: LLM output {summary, reasons[], remedies[]}
        - errors: Any errors encountered during processing
        - final_response: Final response sent to user
        
        Returns:
        {
            "request_id": str,
            "file_path": str (relative to repo root),
            "public_url": str (URL to GET /api/debug/checklist/{request_id}),
            "html_size": int,
            "success": bool
        }
        """
        try:
            # Build checklist sections
            sections = self._build_sections(
                request_id=request_id,
                session_id=session_id,
                user_input=user_input,
                birth_details=birth_details,
                intent_data=intent_data,
                time_context=time_context,
                api_calls=api_calls,
                reading_pack=reading_pack,
                llm_metadata=llm_metadata,
                llm_response=llm_response,
                errors=errors,
                final_response=final_response
            )
            
            # Generate HTML
            html_content = self._render_html(request_id, sections)
            
            # Write HTML to file
            html_file_path = self.checklists_dir / f"{request_id}.html"
            html_file_path.write_text(html_content, encoding='utf-8')
            
            # Also save metadata as JSON for /api/processing/checklist endpoint
            metadata_dict = {
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "user_input": user_input[:500] if user_input else "",
                "topic": intent_data.get('topic') if intent_data else 'general',
                "mode": intent_data.get('mode') if intent_data else 'ERROR',
                "action_id": intent_data.get('action_id') if intent_data else None,
                "birth_details": birth_details or {},
                "api_calls": api_calls or [],
                "reading_pack": reading_pack or {},
                "llm": llm_metadata or {"model": "niro"},
                "final": {
                    "status": "ok" if not errors else "error",
                    "summary": (llm_response or {}).get('summary', '') if llm_response else ""
                }
            }
            
            metadata_file_path = self.checklists_dir / f"{request_id}.json"
            metadata_file_path.write_text(json.dumps(metadata_dict, indent=2), encoding='utf-8')
            
            file_size = len(html_content)
            logger.info(f"[CHECKLIST] Generated report {request_id}, size={file_size}")
            
            return {
                "request_id": request_id,
                "file_path": f"logs/checklists/{request_id}.html",
                "public_url": f"/api/debug/checklist/{request_id}",
                "html_size": file_size,
                "success": True
            }
        
        except Exception as e:
            logger.error(f"[CHECKLIST] Error generating report for {request_id}: {e}", exc_info=True)
            return {
                "request_id": request_id,
                "file_path": None,
                "public_url": None,
                "html_size": 0,
                "success": False,
                "error": str(e)
            }
    
    def _build_sections(
        self,
        request_id: str,
        session_id: str,
        user_input: str,
        birth_details: Optional[Dict] = None,
        intent_data: Optional[Dict] = None,
        time_context: Optional[Dict] = None,
        api_calls: Optional[List[Dict]] = None,
        reading_pack: Optional[Dict] = None,
        llm_metadata: Optional[Dict] = None,
        llm_response: Optional[Dict] = None,
        errors: Optional[List[str]] = None,
        final_response: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Build checklist sections"""
        
        return {
            "metadata": {
                "request_id": request_id,
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "title": f"NIRO Request Checklist #{request_id}"
            },
            "input": {
                "user_message": user_input[:500] if user_input else "(empty)",
                "birth_details": self._format_birth_details(birth_details),
                "intent": intent_data or {},
                "time_context": time_context or {}
            },
            "processing": {
                "api_calls": api_calls or [],
                "reading_pack": reading_pack or {},
                "llm_metadata": llm_metadata or {},
                "errors": errors or []
            },
            "output": {
                "llm_response": llm_response or {},
                "final_response": final_response or {}
            }
        }
    
    def _format_birth_details(self, birth_details: Optional[Dict]) -> Dict:
        """Format birth details for display"""
        if not birth_details:
            return {"status": "Not provided"}
        
        return {
            "date_of_birth": birth_details.get("dob", "?"),
            "time_of_birth": birth_details.get("tob", "?"),
            "location": birth_details.get("location", "?"),
            "coordinates": f"{birth_details.get('lat', '?')}, {birth_details.get('lon', '?')}",
            "timezone": birth_details.get("tz", "?")
        }
    
    def _render_html(self, request_id: str, sections: Dict[str, Any]) -> str:
        """
        Render complete HTML checklist report.
        """
        metadata = sections["metadata"]
        input_sec = sections["input"]
        proc_sec = sections["processing"]
        output_sec = sections["output"]
        
        # Build API calls table
        api_calls_html = self._render_api_calls_table(proc_sec["api_calls"])
        
        # Build errors section
        errors_html = self._render_errors_section(proc_sec["errors"])
        
        # Build reading pack summary
        reading_html = self._render_reading_pack(proc_sec["reading_pack"])
        
        # Build LLM section
        llm_html = self._render_llm_section(proc_sec["llm_metadata"], output_sec["llm_response"])
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{metadata['title']}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
        }}
        .header p {{
            font-size: 14px;
            opacity: 0.9;
        }}
        .content {{
            padding: 40px;
        }}
        .section {{
            margin-bottom: 40px;
        }}
        .section-title {{
            font-size: 20px;
            font-weight: 600;
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }}
        .checklist-item {{
            display: flex;
            align-items: flex-start;
            margin-bottom: 15px;
            padding: 15px;
            background: #f8f9ff;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        .checkbox {{
            width: 20px;
            height: 20px;
            min-width: 20px;
            margin-right: 15px;
            margin-top: 2px;
            border-radius: 4px;
            background: #667eea;
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: bold;
        }}
        .checkbox.unchecked {{
            background: #ccc;
        }}
        .checkbox-label {{
            flex: 1;
        }}
        .label-title {{
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        }}
        .label-value {{
            color: #666;
            font-size: 14px;
            word-break: break-word;
        }}
        .status-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            margin-right: 10px;
        }}
        .status-success {{
            background: #c8e6c9;
            color: #2e7d32;
        }}
        .status-error {{
            background: #ffcdd2;
            color: #c62828;
        }}
        .status-warning {{
            background: #fff3cd;
            color: #856404;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        th {{
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}
        td {{
            padding: 12px;
            border-bottom: 1px solid #eee;
        }}
        tr:hover {{
            background: #f8f9ff;
        }}
        .code-block {{
            background: #f5f5f5;
            padding: 12px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            overflow-x: auto;
            color: #333;
        }}
        .error-box {{
            background: #ffebee;
            border-left: 4px solid #f44336;
            padding: 15px;
            border-radius: 4px;
            margin: 10px 0;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            font-size: 12px;
            color: #999;
            border-top: 1px solid #eee;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✨ NIRO Request Checklist</h1>
            <p>Request ID: <code>{metadata['request_id']}</code></p>
            <p>{metadata['timestamp']}</p>
        </div>
        
        <div class="content">
            <!-- INPUT SECTION -->
            <div class="section">
                <div class="section-title">📝 User Input</div>
                
                <div class="checklist-item">
                    <div class="checkbox">✓</div>
                    <div class="checkbox-label">
                        <div class="label-title">User Message</div>
                        <div class="label-value">{self._escape_html(input_sec.get('user_message', '(none)'))}</div>
                    </div>
                </div>
                
                <div class="checklist-item">
                    <div class="checkbox{'' if input_sec.get('birth_details', {}).get('date_of_birth') != '?' else ' unchecked'}">
                        {self._checkbox_icon(input_sec.get('birth_details', {}).get('date_of_birth') != '?')}
                    </div>
                    <div class="checkbox-label">
                        <div class="label-title">Birth Details</div>
                        <div class="label-value">
                            DOB: {input_sec.get('birth_details', {}).get('date_of_birth', '?')}<br>
                            TOB: {input_sec.get('birth_details', {}).get('time_of_birth', '?')}<br>
                            Location: {input_sec.get('birth_details', {}).get('location', '?')}<br>
                            Coordinates: {input_sec.get('birth_details', {}).get('coordinates', '?')}<br>
                            Timezone: {input_sec.get('birth_details', {}).get('timezone', '?')}
                        </div>
                    </div>
                </div>
                
                <div class="checklist-item">
                    <div class="checkbox{'' if input_sec.get('intent', {}).get('topic') else ' unchecked'}">
                        {self._checkbox_icon(bool(input_sec.get('intent', {}).get('topic')))}
                    </div>
                    <div class="checkbox-label">
                        <div class="label-title">Intent Classification</div>
                        <div class="label-value">
                            Topic: {input_sec.get('intent', {}).get('topic', '(none)')}<br>
                            Mode: {input_sec.get('intent', {}).get('mode', '(none)')}
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- PROCESSING SECTION -->
            <div class="section">
                <div class="section-title">⚙️ Processing Pipeline</div>
                
                <div class="checklist-item">
                    <div class="checkbox">ℹ️</div>
                    <div class="checkbox-label">
                        <div class="label-title">API Calls Summary</div>
                        <div class="label-value">
                            Total: {len(proc_sec.get('api_calls', []))} calls
                        </div>
                    </div>
                </div>
                
                {api_calls_html}
                
                {reading_html}
                
                {llm_html}
            </div>
            
            <!-- ERRORS SECTION -->
            {errors_html}
            
            <!-- OUTPUT SECTION -->
            <div class="section">
                <div class="section-title">📤 Final Response</div>
                
                <div class="checklist-item">
                    <div class="checkbox">✓</div>
                    <div class="checkbox-label">
                        <div class="label-title">Response Status</div>
                        <div class="label-value">
                            <span class="status-badge status-success">OK</span>
                            Request processed successfully.
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>This checklist was auto-generated by NIRO Observability Pipeline</p>
            <p>Session ID: {input_sec.get('session_id', '?')} | Request ID: {metadata['request_id']}</p>
        </div>
    </div>
</body>
</html>"""
        
        return html
    
    def _render_api_calls_table(self, api_calls: List[Dict]) -> str:
        """Render API calls as table"""
        if not api_calls:
            return '<div class="checklist-item"><div class="checkbox unchecked">○</div><div class="checkbox-label"><div class="label-title">No API Calls</div></div></div>'
        
        rows = ""
        for call in api_calls:
            status = call.get("status", "unknown")
            status_class = "status-success" if status in ["200", 200, "ok", "success"] else "status-error"
            
            rows += f"""
                <tr>
                    <td><strong>{call.get('endpoint', '?')}</strong></td>
                    <td><span class="status-badge {status_class}">{status}</span></td>
                    <td>{call.get('duration_ms', '?')}ms</td>
                    <td>{self._escape_html(call.get('error', '-'))}</td>
                </tr>
            """
        
        return f"""
            <div class="checklist-item">
                <div class="checkbox">📡</div>
                <div class="checkbox-label">
                    <div class="label-title">API Calls ({len(api_calls)})</div>
                    <table>
                        <tr>
                            <th>Endpoint</th>
                            <th>Status</th>
                            <th>Duration</th>
                            <th>Error</th>
                        </tr>
                        {rows}
                    </table>
                </div>
            </div>
        """
    
    def _render_reading_pack(self, reading_pack: Dict) -> str:
        """Render reading pack summary"""
        if not reading_pack:
            return ""
        
        return f"""
            <div class="checklist-item">
                <div class="checkbox">📊</div>
                <div class="checkbox-label">
                    <div class="label-title">Astro Signals Summary</div>
                    <div class="label-value">
                        Signals Kept: {reading_pack.get('kept_count', 0)}<br>
                        Signals Dropped: {reading_pack.get('dropped_count', 0)}<br>
                        Top Signal: {reading_pack.get('top_signal', '(none)')}
                    </div>
                </div>
            </div>
        """
    
    def _render_llm_section(self, llm_metadata: Dict, llm_response: Dict) -> str:
        """Render LLM processing section"""
        if not llm_metadata and not llm_response:
            return ""
        
        model = llm_metadata.get("model", "?")
        tokens_prompt = llm_metadata.get("tokens_prompt", "?")
        tokens_completion = llm_metadata.get("tokens_completion", "?")
        
        summary = llm_response.get("summary", "(no summary)")
        
        return f"""
            <div class="checklist-item">
                <div class="checkbox">🧠</div>
                <div class="checkbox-label">
                    <div class="label-title">LLM Processing (Model: {model})</div>
                    <div class="label-value">
                        Tokens In: {tokens_prompt} | Tokens Out: {tokens_completion}<br>
                        Summary: {self._escape_html(summary[:200])}...
                    </div>
                </div>
            </div>
        """
    
    def _render_errors_section(self, errors: List[str]) -> str:
        """Render errors section if any"""
        if not errors:
            return ""
        
        error_items = "".join(f'<div class="error-box">{self._escape_html(e)}</div>' for e in errors)
        
        return f"""
            <div class="section">
                <div class="section-title">⚠️ Errors Encountered</div>
                <div class="checklist-item">
                    <div class="checkbox unchecked">✗</div>
                    <div class="checkbox-label">
                        <div class="label-title">Error Details ({len(errors)})</div>
                        {error_items}
                    </div>
                </div>
            </div>
        """
    
    @staticmethod
    def _escape_html(text: str) -> str:
        """Escape HTML special characters"""
        if not isinstance(text, str):
            text = str(text)
        return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;"))
    
    @staticmethod
    def _checkbox_icon(checked: bool) -> str:
        """Return checkbox icon"""
        return "✓" if checked else "○"
    
    def read_report(self, request_id: str) -> Optional[str]:
        """
        Read and return HTML report content.
        
        Used by GET /api/debug/checklist/{request_id} endpoint.
        """
        file_path = self.checklists_dir / f"{request_id}.html"
        
        if not file_path.exists():
            logger.warning(f"[CHECKLIST] Report not found: {request_id}")
            return None
        
        try:
            content = file_path.read_text(encoding='utf-8')
            logger.info(f"[CHECKLIST] Report served: {request_id}")
            return content
        
        except Exception as e:
            logger.error(f"[CHECKLIST] Error reading report {request_id}: {e}")
            return None


# Singleton instance
_checklist_report = None

def get_checklist_report() -> ChecklistReport:
    """Get or create singleton ChecklistReport instance"""
    global _checklist_report
    if _checklist_report is None:
        _checklist_report = ChecklistReport()
    return _checklist_report
