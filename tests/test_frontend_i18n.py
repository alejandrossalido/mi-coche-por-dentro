from pathlib import Path

from analysis.report_generator import ReportGenerator
from backend.main import AiQueryRequest


ROOT = Path(__file__).resolve().parents[1]
I18N = (ROOT / "dashboard/src/lib/i18n.tsx").read_text(encoding="utf-8")


def test_four_languages_are_declared_and_spanish_is_default():
    for language in ("es", "en", "it", "de"):
        assert f"id: '{language}'" in I18N
    assert "useState<AppLanguage>('es')" in I18N
    assert "micoche-language" in I18N


def test_language_provider_and_both_selectors_are_installed():
    layout = (ROOT / "dashboard/src/app/layout.tsx").read_text(encoding="utf-8")
    header = (ROOT / "dashboard/src/components/Header.tsx").read_text(encoding="utf-8")
    onboarding = (ROOT / "dashboard/src/components/OnboardingDialog.tsx").read_text(encoding="utf-8")
    assert "<LanguageProvider>" in layout
    assert "<LanguageSelector" in header
    assert "Select your language / Selecciona tu idioma" in onboarding
    assert "<LanguageSelector expanded />" in onboarding


def test_locale_sensitive_features_follow_the_selected_language():
    assistant = (ROOT / "dashboard/src/components/AiAssistantPanel.tsx").read_text(encoding="utf-8")
    page = (ROOT / "dashboard/src/app/page.tsx").read_text(encoding="utf-8")
    assert "recognition.lang = speechLocale" in assistant
    assert "toLocaleString(locale)" in assistant
    assert "language," in assistant
    assert "report?lang=${language}" in page


def test_technical_pid_labels_exist_in_every_added_language():
    labels = (ROOT / "dashboard/src/lib/telemetryLabels.ts").read_text(encoding="utf-8")
    for language in ("en", "it", "de"):
        assert f"{language}: {{" in labels
    for pid in ("RPM", "VAG_INJECTION_QUANTITY", "VAG_DPF_SOOT_CALCULATED"):
        assert labels.count(f"{pid}:") >= 3


def test_backend_accepts_language_and_report_localizes_headings():
    assert AiQueryRequest(question="test", language="de").language == "de"
    html = ReportGenerator.generate_html_report(
        vehicle={"display_name": "Testwagen"},
        session={"id": "s1"},
        stats={"signals": {}},
        findings=[],
        mode="user",
        language="en",
    )
    assert '<html lang="en">' in html
    assert "Driver diagnostic summary" in html
    assert "Average consumption" in html


def test_dynamic_profiles_and_composite_values_are_localized():
    wizard = (ROOT / "dashboard/src/components/GuidedTestWizard.tsx").read_text(encoding="utf-8")
    symptom_guide = (ROOT / "dashboard/src/components/SymptomGuide.tsx").read_text(encoding="utf-8")
    assert "t(profile.name)" in wizard
    assert "t(selected.description)" in wizard
    assert "t(activeStep?.title" in wizard
    assert "t(recommended?.name" in symptom_guide
    for text in (
        "Batería y alternador",
        "Termostato y refrigeración",
        "Estabilidad de Ralentí",
        "Turbo y admisión",
        "Consumo e inyección",
        "Emisiones / ITV",
        "Registrador multicanal // señales sincronizadas",
    ):
        assert f"'{text}':" in I18N
    assert "señales objetivo$/" in I18N
    assert "no es OBD$/" in I18N


def test_i18n_source_coverage_checker_is_part_of_the_build_tooling():
    package = (ROOT / "dashboard/package.json").read_text(encoding="utf-8")
    checker = ROOT / "dashboard/scripts/check-i18n.mjs"
    assert checker.exists()
    assert '"i18n:check"' in package
