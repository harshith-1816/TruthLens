"""
TruthLens - Forensic Report Generator
Generates structured JSON forensic reports, markdown summaries, and publication-ready
HTML forensic dossiers featuring flagged evidence cards, cross-modal context, and chain of custody.
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional
from core.models import (
    ForensicReport,
    CalibratedAssessment,
    ModalityAnalysisResult,
    CrossModalFinding,
    ForensicIndicator,
    ChainOfCustodyRecord
)


class ForensicReportGenerator:
    """Produces structured forensic reports across JSON, Markdown, and HTML formats."""

    def build_report(
        self,
        case_title: str,
        investigator: str,
        assessment: CalibratedAssessment,
        modality_results: Dict[str, ModalityAnalysisResult],
        cross_modal_findings: List[CrossModalFinding],
        custody_records: List[ChainOfCustodyRecord],
        case_id: Optional[str] = None
    ) -> ForensicReport:
        report_id = f"TL-REP-{uuid.uuid4().hex[:8].upper()}"
        active_case_id = case_id or f"CASE-{uuid.uuid4().hex[:6].upper()}"

        all_indicators: List[ForensicIndicator] = []
        for res in modality_results.values():
            all_indicators.extend(res.indicators)

        return ForensicReport(
            report_id=report_id,
            case_title=case_title,
            case_id=active_case_id,
            investigator=investigator,
            created_at=datetime.now(timezone.utc).isoformat(),
            assessment=assessment,
            modality_results=modality_results,
            cross_modal_findings=cross_modal_findings,
            all_indicators=all_indicators,
            chain_of_custody=custody_records
        )

    def to_json(self, report: ForensicReport, indent: int = 2) -> str:
        """Serializes report to structured JSON string."""
        return report.model_dump_json(indent=indent)

    def to_markdown(self, report: ForensicReport) -> str:
        """Generates a comprehensive markdown forensic dossier."""
        lines = []
        lines.append(f"# Forensic Examination Report: {report.case_title}")
        lines.append(f"**Report ID**: `{report.report_id}` | **Case ID**: `{report.case_id}` | **Investigator**: {report.investigator}")
        lines.append(f"**Generated**: {report.created_at} UTC\n")

        lines.append("## 1. Executive Summary & Calibrated Verdict")
        lines.append(f"- **Verdict**: `{report.assessment.overall_verdict.value}`")
        lines.append(f"- **Manipulation Probability Score**: **{report.assessment.overall_manipulation_score} / 100**")
        lines.append(f"- **Calibrated Certainty/Confidence**: **{report.assessment.calibrated_confidence}%**")
        lines.append(f"\n> {report.assessment.evidential_summary}\n")

        lines.append("### Modality Risk Breakdown")
        for mod, sc in report.assessment.modality_breakdown.items():
            lines.append(f"- **{mod.upper()}**: {sc}/100")
        lines.append("")

        lines.append("## 2. Cross-Modal Correlation Findings")
        if not report.cross_modal_findings:
            lines.append("*No cross-modal correlations established.*")
        else:
            for f in report.cross_modal_findings:
                lines.append(f"### [{f.status}] {f.description}")
                lines.append(f"- **Modalities Involved**: {', '.join([m.value for m in f.modalities_involved])}")
                lines.append(f"- **Risk Impact**: `{f.risk_impact}` (Confidence: {int(f.confidence * 100)}%)")
                lines.append(f"- **Technical Details**: {f.details}\n")

        lines.append("## 3. Flagged Evidence & Detected Indicators")
        if not report.all_indicators:
            lines.append("*No suspicious indicators flagged.*")
        else:
            for ind in report.all_indicators:
                lines.append(f"### [{ind.severity.value}] {ind.title}")
                lines.append(f"- **Modality**: `{ind.modality.value}` | **Category**: `{ind.category.value}`")
                lines.append(f"- **Suspicion Score**: {int(ind.suspicion_score * 100)}% | **Confidence**: {int(ind.confidence * 100)}%")
                lines.append(f"- **Description**: {ind.description}")
                lines.append(f"- **Technical Details**: {ind.technical_details}")
                if ind.evidence_ref:
                    lines.append(f"- **Trace Reference**: File `{ind.evidence_ref.source_filename}` (`{ind.evidence_ref.location_type}`: {ind.evidence_ref.location_value})")
                lines.append("")

        lines.append("## 4. Uncertainty, Caveats & Alternative Explanations")
        lines.append("### Known Uncertainty Factors & Limitations")
        for u in report.assessment.uncertainty_factors:
            lines.append(f"- {u}")
        lines.append("\n### Plausible Alternative Explanations")
        for a in report.assessment.alternative_explanations:
            lines.append(f"- {a}")

        lines.append("\n## 5. Recommended Human Examiner Checklist")
        for chk in report.assessment.recommended_human_checks:
            lines.append(f"- [ ] {chk}")

        lines.append("\n## 6. Chain of Custody & Traceability Log")
        lines.append("| Timestamp (UTC) | Action | Performed By | File Name | SHA-256 Hash |")
        lines.append("| --- | --- | --- | --- | --- |")
        for rec in report.chain_of_custody:
            short_hash = f"{rec.sha256[:10]}...{rec.sha256[-8:]}" if len(rec.sha256) > 20 else rec.sha256
            lines.append(f"| {rec.timestamp} | {rec.event} | {rec.performed_by} | `{rec.file_name}` | `{short_hash}` |")

        lines.append(f"\n---\n*Disclaimer*: {report.disclaimer}")
        return "\n".join(lines)

    def to_html_dossier(self, report: ForensicReport) -> str:
        """Generates a standalone, styled HTML forensic report."""
        verdict_color = "#ef4444" if "MANIPULATION" in report.assessment.overall_verdict.value else (
            "#f59e0b" if "SUSPICIOUS" in report.assessment.overall_verdict.value else "#10b981"
        )

        indicators_html = ""
        for ind in report.all_indicators:
            badge_bg = {
                "CRITICAL": "#ef4444",
                "HIGH": "#f97316",
                "MEDIUM": "#eab308",
                "LOW": "#3b82f6",
                "INFO": "#64748b"
            }.get(ind.severity.value, "#64748b")

            loc_str = ""
            if ind.evidence_ref:
                loc_str = f"""
                <div class="evidence-trace">
                    <strong>Source File:</strong> <code>{ind.evidence_ref.source_filename}</code> | 
                    <strong>Target:</strong> <code>{ind.evidence_ref.location_type}</code>: {json.dumps(ind.evidence_ref.location_value)}
                </div>
                """

            indicators_html += f"""
            <div class="indicator-card">
                <div class="indicator-header">
                    <span class="badge" style="background:{badge_bg};">{ind.severity.value}</span>
                    <span class="indicator-modality">[{ind.modality.value.upper()}]</span>
                    <strong>{ind.title}</strong>
                </div>
                <p class="indicator-desc">{ind.description}</p>
                <div class="tech-box">
                    <small><strong>Technical Findings:</strong> {ind.technical_details}</small>
                </div>
                {loc_str}
            </div>
            """

        cross_modal_html = ""
        for cm in report.cross_modal_findings:
            cm_color = "#ef4444" if cm.risk_impact == "INCREASES_RISK" else "#10b981"
            cross_modal_html += f"""
            <div class="cm-card" style="border-left: 4px solid {cm_color};">
                <div class="cm-header">
                    <span class="cm-status">[{cm.status}]</span>
                    <strong>{cm.description}</strong>
                </div>
                <p>{cm.details}</p>
                <div class="cm-meta">
                    <span>Modalities: <code>{', '.join([m.value for m in cm.modalities_involved])}</code></span>
                    <span>Risk Impact: <strong style="color:{cm_color};">{cm.risk_impact}</strong></span>
                    <span>Confidence: {int(cm.confidence * 100)}%</span>
                </div>
            </div>
            """

        visualizations_html = ""
        for mod_name, res in report.modality_results.items():
            if res.visualizations:
                visualizations_html += f"<h3>{mod_name.upper()} Forensic Visualizations</h3><div class='viz-grid'>"
                for k, v in res.visualizations.items():
                    visualizations_html += f"""
                    <div class="viz-card">
                        <h4>{k.replace('_', ' ').title()}</h4>
                        <img src="{v}" alt="{k}" />
                    </div>
                    """
                visualizations_html += "</div>"

        custody_rows = ""
        for rec in report.chain_of_custody:
            custody_rows += f"""
            <tr>
                <td>{rec.timestamp}</td>
                <td>{rec.event}</td>
                <td><code>{rec.file_name}</code></td>
                <td><code title="{rec.sha256}">{rec.sha256[:16]}...</code></td>
                <td>{rec.performed_by}</td>
            </tr>
            """

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>TruthLens Forensic Dossier - {report.report_id}</title>
<style>
    body {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        background-color: #0f172a;
        color: #f1f5f9;
        margin: 0;
        padding: 30px;
        line-height: 1.5;
    }}
    .container {{
        max-width: 1050px;
        margin: 0 auto;
        background: #1e293b;
        padding: 36px;
        border-radius: 12px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
    }}
    .header {{
        border-bottom: 2px solid #334155;
        padding-bottom: 20px;
        margin-bottom: 25px;
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
    }}
    .title {{ margin: 0; font-size: 24px; color: #38bdf8; }}
    .subtitle {{ color: #94a3b8; font-size: 14px; margin-top: 4px; }}
    .badge {{
        display: inline-block;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 700;
        color: #fff;
    }}
    .verdict-banner {{
        background: #0f172a;
        border: 2px solid {verdict_color};
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 30px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    .score-circle {{
        font-size: 32px;
        font-weight: bold;
        color: {verdict_color};
    }}
    .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px; }}
    .panel {{
        background: #182234;
        padding: 18px;
        border-radius: 8px;
        border: 1px solid #334155;
    }}
    .panel h3 {{ margin-top: 0; font-size: 16px; color: #38bdf8; border-bottom: 1px solid #334155; padding-bottom: 8px; }}
    .indicator-card, .cm-card {{
        background: #182234;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 14px;
        margin-bottom: 14px;
    }}
    .indicator-header, .cm-header {{
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 8px;
    }}
    .tech-box {{
        background: #0f172a;
        padding: 8px 12px;
        border-radius: 6px;
        margin-top: 8px;
        font-family: monospace;
        font-size: 12px;
    }}
    .evidence-trace {{
        margin-top: 8px;
        font-size: 12px;
        color: #94a3b8;
    }}
    .viz-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
        gap: 16px;
        margin-bottom: 25px;
    }}
    .viz-card {{
        background: #0f172a;
        padding: 12px;
        border-radius: 8px;
        border: 1px solid #334155;
        text-align: center;
    }}
    .viz-card img {{
        max-width: 100%;
        border-radius: 6px;
        margin-top: 8px;
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
        margin-top: 10px;
    }}
    th, td {{
        padding: 10px;
        text-align: left;
        border-bottom: 1px solid #334155;
    }}
    th {{ background: #0f172a; color: #94a3b8; }}
    code {{ background: #0f172a; padding: 2px 6px; border-radius: 4px; font-family: monospace; font-size: 12px; color: #e2e8f0; }}
    .disclaimer {{
        margin-top: 35px;
        padding: 14px;
        border-left: 4px solid #64748b;
        background: #0f172a;
        font-size: 12px;
        color: #94a3b8;
    }}
</style>
</head>
<body>
<div class="container">
    <div class="header">
        <div>
            <h1 class="title">TruthLens Multimodal Forensic Dossier</h1>
            <div class="subtitle">Case: <strong>{report.case_title}</strong> (ID: {report.case_id})</div>
        </div>
        <div style="text-align:right;">
            <div><strong>Report ID:</strong> <code>{report.report_id}</code></div>
            <div class="subtitle">Investigator: {report.investigator}</div>
            <div class="subtitle">{report.created_at} UTC</div>
        </div>
    </div>

    <div class="verdict-banner">
        <div>
            <h2 style="margin:0 0 6px 0; color:{verdict_color};">{report.assessment.overall_verdict.value}</h2>
            <p style="margin:0; color:#cbd5e1; max-width:650px;">{report.assessment.evidential_summary}</p>
        </div>
        <div style="text-align:center;">
            <div class="score-circle">{report.assessment.overall_manipulation_score} <span style="font-size:16px; color:#94a3b8;">/ 100</span></div>
            <div style="font-size:12px; color:#94a3b8;">Calibrated Confidence: <strong>{report.assessment.calibrated_confidence}%</strong></div>
        </div>
    </div>

    <div class="grid-2">
        <div class="panel">
            <h3>Forensic Modality Breakdown</h3>
            <ul>
                {"".join([f"<li><strong>{m.upper()}</strong>: {sc}/100</li>" for m, sc in report.assessment.modality_breakdown.items()])}
            </ul>
        </div>
        <div class="panel">
            <h3>Alternative Explanations (Caveats)</h3>
            <ul>
                {"".join([f"<li>{a}</li>" for a in report.assessment.alternative_explanations])}
            </ul>
        </div>
    </div>

    <h2>Cross-Modal Correlation Matrix</h2>
    {cross_modal_html or "<p>No cross-modal findings generated.</p>"}

    <h2>Detected Forensic Indicators & Flagged Regions</h2>
    {indicators_html or "<p>No manipulation indicators flagged.</p>"}

    {visualizations_html}

    <h2>Recommended Human Forensic Verification Checklist</h2>
    <div class="panel">
        <ul>
            {"".join([f"<li>[ ] {chk}</li>" for chk in report.assessment.recommended_human_checks])}
        </ul>
    </div>

    <h2>Evidentiary Chain of Custody</h2>
    <table>
        <thead>
            <tr>
                <th>Timestamp (UTC)</th>
                <th>Action</th>
                <th>File Name</th>
                <th>SHA-256 Hash</th>
                <th>Examiner / Node</th>
            </tr>
        </thead>
        <tbody>
            {custody_rows}
        </tbody>
    </table>

    <div class="disclaimer">
        <strong>Forensic Evidentiary Disclaimer:</strong> {report.disclaimer}
    </div>
</div>
</body>
</html>
"""
        return html
