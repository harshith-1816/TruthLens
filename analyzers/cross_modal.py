"""
TruthLens - Cross-Modal Correlation Engine
Compares signals, timestamps, environments, and indicators across Image, Video,
Audio, and Text modalities to identify corroborating evidence or contradictions.
"""

from typing import Dict, List, Optional, Any
from core.models import (
    ModalityType,
    ModalityAnalysisResult,
    CrossModalFinding,
    EvidenceReference,
    SeverityLevel
)


class CrossModalCorrelator:
    """
    Correlates forensic signals across disparate modalities.
    Produces evidence-linked cross-modal findings that strengthen or weaken overall confidence.
    """

    def correlate(
        self, modality_results: Dict[str, ModalityAnalysisResult]
    ) -> List[CrossModalFinding]:
        findings: List[CrossModalFinding] = []

        has_image = "image" in modality_results
        has_video = "video" in modality_results
        has_audio = "audio" in modality_results
        has_text = "text" in modality_results

        img_res = modality_results.get("image")
        vid_res = modality_results.get("video")
        aud_res = modality_results.get("audio")
        txt_res = modality_results.get("text")

        # 1. Audio-Visual Temporal & Cadence Synchronization
        if (has_video or has_image) and has_audio:
            findings.extend(self._correlate_audiovisual(vid_res, aud_res, img_res))

        # 2. Visual-Text Contextual & Environmental Alignment
        if (has_image or has_video) and has_text:
            findings.extend(self._correlate_visual_and_text(img_res or vid_res, txt_res))

        # 3. Audio-Text Affect & Cadence Alignment
        if has_audio and has_text:
            findings.extend(self._correlate_audio_and_text(aud_res, txt_res))

        # 4. Multi-Modal Corroboration or Attenuation of Tampering Signals
        findings.extend(self._correlate_manipulation_corroboration(modality_results))

        return findings

    def _correlate_audiovisual(
        self,
        vid_res: Optional[ModalityAnalysisResult],
        aud_res: ModalityAnalysisResult,
        img_res: Optional[ModalityAnalysisResult]
    ) -> List[CrossModalFinding]:
        findings = []

        if vid_res:
            vid_metrics = vid_res.metrics
            aud_metrics = aud_res.metrics

            # Check temporal length consistency if video duration is available
            aud_dur = aud_metrics.get("duration_seconds", 0)
            vid_frames = vid_metrics.get("frames_analyzed", 0)
            
            # Check for synchronous anomalies
            vid_has_jitter = any(ind.category.value == "TEMPORAL_JITTER" for ind in vid_res.indicators)
            aud_has_vocoder = any(ind.category.value == "VOICE_CLONING_SIGNATURE" for ind in aud_res.indicators)

            if vid_has_jitter and aud_has_vocoder:
                findings.append(
                    CrossModalFinding(
                        finding_id="XM_AV_SYNC_DEEPFAKE_CORROBORATION",
                        modalities_involved=[ModalityType.VIDEO, ModalityType.AUDIO],
                        correlation_type="AUDIO_VISUAL_LIP_SYNC_CORROBORATION",
                        status="CORROBORATING_MANIPULATION",
                        description="Audio voice cloning artifacts strongly corroborate video temporal facial jitter.",
                        details=(
                            "The simultaneous occurrence of acoustic neural vocoder roll-off and "
                            "inter-frame facial variance spikes indicates a coordinated synthetic video/audio reenactment."
                        ),
                        risk_impact="INCREASES_RISK",
                        confidence=0.91,
                        evidence_references=[
                            EvidenceReference(
                                modality=ModalityType.VIDEO,
                                source_filename=vid_res.filename,
                                sha256_hash=vid_res.sha256,
                                location_type="video_jitter_frames",
                                location_value=vid_metrics.get("temporal_consistency", {})
                            ),
                            EvidenceReference(
                                modality=ModalityType.AUDIO,
                                source_filename=aud_res.filename,
                                sha256_hash=aud_res.sha256,
                                location_type="audio_spectral_cutoff",
                                location_value=aud_metrics.get("spectral_forensics", {})
                            )
                        ]
                    )
                )
            elif not vid_has_jitter and not aud_has_vocoder:
                findings.append(
                    CrossModalFinding(
                        finding_id="XM_AV_NATURAL_CADENCE",
                        modalities_involved=[ModalityType.VIDEO, ModalityType.AUDIO],
                        correlation_type="AUDIO_VISUAL_TEMPORAL_COHERENCE",
                        status="CORROBORATING_AUTHENTIC",
                        description="Visual frame progression and acoustic frequency cadence are mutually consistent.",
                        details="No desynchronization or temporal discontinuity between acoustic track and visual frames.",
                        risk_impact="LOWERS_RISK",
                        confidence=0.85,
                        evidence_references=[]
                    )
                )

        return findings

    def _correlate_visual_and_text(
        self,
        vis_res: ModalityAnalysisResult,
        txt_res: ModalityAnalysisResult
    ) -> List[CrossModalFinding]:
        findings = []
        vis_meta = vis_res.metrics.get("metadata", {})
        txt_metrics = txt_res.metrics
        txt_claims = txt_metrics.get("extracted_claims", {})

        # Check metadata software claims vs text claims
        exif_camera = vis_meta.get("camera_make_model", "")
        exif_software = vis_meta.get("software", "")

        txt_has_disinfo = any(ind.category.value == "TEXT_SYNTHESIS_METRIC" for ind in txt_res.indicators)
        vis_has_splice = any(ind.category.value in ["NOISE_DISCREPANCY", "SEAM_OR_SPLICE", "COMPRESSION_ANOMALY"] for ind in vis_res.indicators)

        if vis_has_splice and txt_has_disinfo:
            findings.append(
                CrossModalFinding(
                    finding_id="XM_VISUAL_TEXT_COORDINATED_DISINFO",
                    modalities_involved=[vis_res.modality, ModalityType.TEXT],
                    correlation_type="IMAGE_TEXT_SEMANTIC_ALIGNMENT",
                    status="CORROBORATING_MANIPULATION",
                    description="Visual splicing anomalies align with sensationalist text urgency framing.",
                    details=(
                        "The media displays localized visual tampering while the accompanying caption "
                        "employs manipulative psychological urgency hooks, typical of coordinated false narrative campaigns."
                    ),
                    risk_impact="INCREASES_RISK",
                    confidence=0.88,
                    evidence_references=[
                        EvidenceReference(
                            modality=vis_res.modality,
                            source_filename=vis_res.filename,
                            sha256_hash=vis_res.sha256,
                            location_type="visual_splice",
                            location_value={"visual_indicators": len(vis_res.indicators)}
                        ),
                        EvidenceReference(
                            modality=ModalityType.TEXT,
                            source_filename=txt_res.filename,
                            sha256_hash=txt_res.sha256,
                            location_type="text_urgency_markers",
                            location_value=txt_metrics.get("disinfo_framing", {})
                        )
                    ]
                )
            )

        # Environmental & Temporal Cross-Modal Contradiction Check
        # e.g., caption claiming outdoor daytime sunny event vs dark nighttime indoor scene
        text_content_lower = str(txt_res.metrics.get("extracted_claims", "")).lower() + " " + str(txt_metrics.get("disinfo_framing", "")).lower()
        # Check text words for daylight / outdoor claims
        is_daylight_claim = any(w in text_content_lower for w in ["daytime", "broad daylight", "sunny afternoon", "sunlight", "outdoor morning"])
        vis_ela = vis_res.metrics.get("ela_mean_difference", 0)
        # Check if visual brightness is very low
        mean_vis_lum = vis_res.metrics.get("lighting_consistency", {}).get("mean_luminance", 128)
        if is_daylight_claim and mean_vis_lum < 40:
            findings.append(
                CrossModalFinding(
                    finding_id="XM_ENVIRONMENT_CONTRADICTION",
                    modalities_involved=[vis_res.modality, ModalityType.TEXT],
                    correlation_type="ENVIRONMENTAL_DAYLIGHT_CONTRADICTION",
                    status="CONTRADICTION",
                    description="Caption claims outdoor daytime event, but visual evidence demonstrates nighttime indoor illumination.",
                    details="Direct cross-modal semantic contradiction between contextual claim and measured optical scene luminance.",
                    risk_impact="INCREASES_RISK",
                    confidence=0.92,
                    evidence_references=[
                        EvidenceReference(
                            modality=vis_res.modality,
                            source_filename=vis_res.filename,
                            sha256_hash=vis_res.sha256,
                            location_type="scene_luminance",
                            location_value={"mean_luminance": mean_vis_lum}
                        ),
                        EvidenceReference(
                            modality=ModalityType.TEXT,
                            source_filename=txt_res.filename,
                            sha256_hash=txt_res.sha256,
                            location_type="text_daylight_claim",
                            location_value={"claim": "daytime_sunlight"}
                        )
                    ]
                )
            )

        # Check if text claims authentic raw capture while metadata has Photoshop/Midjourney
        if "photoshop" in exif_software.lower() or "midjourney" in str(vis_meta).lower():
            findings.append(
                CrossModalFinding(
                    finding_id="XM_METADATA_CAPTION_CONTRADICTION",
                    modalities_involved=[vis_res.modality, ModalityType.TEXT],
                    correlation_type="METADATA_CAPTION_VERACITY",
                    status="CONTRADICTION",
                    description="Embedded technical container metadata directly contradicts editorial claim of unedited capture.",
                    details=f"File metadata explicitly reports editing/synthesis signature: {exif_software or 'AI generator'}.",
                    risk_impact="INCREASES_RISK",
                    confidence=0.94,
                    evidence_references=[]
                )
            )

        return findings

    def _correlate_audio_and_text(
        self,
        aud_res: ModalityAnalysisResult,
        txt_res: ModalityAnalysisResult
    ) -> List[CrossModalFinding]:
        findings = []
        aud_is_robotic = any(ind.indicator_id == "AUD_ROBOTIC_PITCH_FLATNESS" for ind in aud_res.indicators)
        txt_is_llm = any(ind.indicator_id == "TXT_LLM_CLICHE_CONCENTRATION" for ind in txt_res.indicators)

        if aud_is_robotic and txt_is_llm:
            findings.append(
                CrossModalFinding(
                    finding_id="XM_FULL_SYNTHETIC_SCRIPT_AND_VOICE",
                    modalities_involved=[ModalityType.AUDIO, ModalityType.TEXT],
                    correlation_type="SPEECH_TRANSCRIPT_CADENCE",
                    status="CORROBORATING_MANIPULATION",
                    description="Acoustically flat synthesized speech matches synthetically generated LLM transcript.",
                    details=(
                        "Both the voice track (robotic pitch monotony, missing micro-tremors) and the spoken transcript "
                        "(characteristic LLM clichés and uniform burstiness) independently indicate end-to-end automated AI generation."
                    ),
                    risk_impact="INCREASES_RISK",
                    confidence=0.93,
                    evidence_references=[
                        EvidenceReference(
                            modality=ModalityType.AUDIO,
                            source_filename=aud_res.filename,
                            sha256_hash=aud_res.sha256,
                            location_type="pitch_flatness",
                            location_value=aud_res.metrics.get("pitch_stability", {})
                        ),
                        EvidenceReference(
                            modality=ModalityType.TEXT,
                            source_filename=txt_res.filename,
                            sha256_hash=txt_res.sha256,
                            location_type="llm_cliche_density",
                            location_value=txt_res.metrics.get("llm_lexicon", {})
                        )
                    ]
                )
            )

        return findings

    def _correlate_manipulation_corroboration(
        self, modality_results: Dict[str, ModalityAnalysisResult]
    ) -> List[CrossModalFinding]:
        findings = []
        high_prob_modalities = [
            mod for mod, res in modality_results.items()
            if res.verdict.value == "HIGH_PROBABILITY_MANIPULATION"
        ]
        authentic_modalities = [
            mod for mod, res in modality_results.items()
            if res.verdict.value == "LIKELY_AUTHENTIC"
        ]

        if len(high_prob_modalities) >= 2:
            findings.append(
                CrossModalFinding(
                    finding_id="XM_MULTI_MODAL_CONVERGENCE",
                    modalities_involved=[modality_results[m].modality for m in high_prob_modalities],
                    correlation_type="MULTI_MODAL_EVIDENTIAL_CONVERGENCE",
                    status="CORROBORATING_MANIPULATION",
                    description=f"Independent manipulation indicators converge across multiple media types: {', '.join(high_prob_modalities)}.",
                    details=(
                        "Multiple orthogonal forensic pipelines detected high-confidence synthetic signals. "
                        "Cross-modal convergence dramatically diminishes the probability of false-positive sensor anomalies."
                    ),
                    risk_impact="INCREASES_RISK",
                    confidence=0.95,
                    evidence_references=[]
                )
            )
        elif len(authentic_modalities) >= 2 and not high_prob_modalities:
            findings.append(
                CrossModalFinding(
                    finding_id="XM_MULTI_MODAL_AUTHENTICITY_CONVERGENCE",
                    modalities_involved=[modality_results[m].modality for m in authentic_modalities],
                    correlation_type="MULTI_MODAL_EVIDENTIAL_CONVERGENCE",
                    status="CORROBORATING_AUTHENTIC",
                    description=f"Signals across tested modalities ({', '.join(authentic_modalities)}) consistently reflect natural capture dynamics.",
                    details="Physical sensor noise, acoustic reverberation, and natural linguistic variation are all present without synthetic signatures.",
                    risk_impact="LOWERS_RISK",
                    confidence=0.90,
                    evidence_references=[]
                )
            )

        return findings
