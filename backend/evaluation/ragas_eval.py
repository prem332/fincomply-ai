import sys
import os
import json
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    RAGAS_FAITHFULNESS_THRESHOLD,
    RAGAS_ANSWER_RELEVANCY_THRESHOLD,
    RAGAS_CONTEXT_PRECISION_THRESHOLD,
    RAGAS_CONTEXT_RECALL_THRESHOLD,
    RAG_TOP_K,
)
from agents.graph import run_pipeline

logger = logging.getLogger(__name__)

# ── 20 Test Questions ──────────────────────────────────────────────────
# 5 GST + 5 RBI + 5 SEBI + 5 MCA
# ground_truth = verified answer from official circular

GOLDEN_TEST_SET = [
    # GST
    {"query": "What is the GST rate on under-construction residential apartments?",
     "domain": "gst",
     "ground_truth": "5% GST applies on under-construction residential apartments (excluding affordable housing which is 1%)"},
    {"query": "Is GST applicable on export of services?",
     "domain": "gst",
     "ground_truth": "Export of services is zero-rated under GST. IGST is not charged."},
    {"query": "What is the threshold for GST registration?",
     "domain": "gst",
     "ground_truth": "Rs 20 lakh annual turnover for goods and services (Rs 10 lakh for special category states)."},
    {"query": "What is the GST e-invoicing threshold for businesses?",
     "domain": "gst",
     "ground_truth": "E-invoicing is mandatory for businesses with annual turnover above Rs 5 crore."},
    {"query": "How many years can GST ITC be claimed?",
     "domain": "gst",
     "ground_truth": "ITC can be claimed by November 30 of the following financial year or filing of annual return."},

    # RBI
    {"query": "What is the RBI repo rate?",
     "domain": "rbi",
     "ground_truth": "The RBI Monetary Policy Committee determines the repo rate. Check rbi.org.in for current rate."},
    {"query": "What are RBI KYC norms for account opening?",
     "domain": "rbi",
     "ground_truth": "Officially Valid Documents (OVD) required: Aadhaar, passport, driving license, voter ID. Video KYC is permitted."},
    {"query": "What is the RBI limit for digital lending by NBFCs?",
     "domain": "rbi",
     "ground_truth": "NBFCs must follow RBI digital lending guidelines: disbursal only to borrower's bank account, APR disclosure mandatory."},
    {"query": "What is the CRR requirement for scheduled commercial banks?",
     "domain": "rbi",
     "ground_truth": "CRR is set by RBI Monetary Policy Committee. Check latest RBI policy announcement for current rate."},
    {"query": "What are priority sector lending targets for banks?",
     "domain": "rbi",
     "ground_truth": "40% of Adjusted Net Bank Credit for domestic banks. Sub-targets include agriculture (18%) and weaker sections (12%)."},

    # SEBI
    {"query": "What is SEBI insider trading regulation?",
     "domain": "sebi",
     "ground_truth": "SEBI (Prohibition of Insider Trading) Regulations 2015 prohibit trading on unpublished price sensitive information (UPSI)."},
    {"query": "What are SEBI IPO grading requirements?",
     "domain": "sebi",
     "ground_truth": "SEBI does not mandate IPO grading. DRHP filing with SEBI is mandatory for public issues above Rs 10 crore."},
    {"query": "What is the lock-in period for promoters in an IPO?",
     "domain": "sebi",
     "ground_truth": "Minimum 20% promoter holding must be locked in for 18 months. Remaining promoter holding locked in for 6 months."},
    {"query": "What are SEBI mutual fund expense ratio limits?",
     "domain": "sebi",
     "ground_truth": "Total Expense Ratio capped at 2.25% for equity funds (first Rs 500 crore AUM). Reduces as AUM increases."},
    {"query": "What is SEBI FPI registration requirement?",
     "domain": "sebi",
     "ground_truth": "Foreign Portfolio Investors must register with SEBI-designated Designated Depository Participants. Category I/II/III based on investor type."},

    # MCA
    {"query": "What is the annual return filing deadline for private companies?",
     "domain": "mca",
     "ground_truth": "MGT-7 (Annual Return) within 60 days of AGM. AOC-4 (Financial Statements) within 30 days of AGM."},
    {"query": "What is the penalty for late filing of annual return?",
     "domain": "mca",
     "ground_truth": "Additional fee of Rs 100 per day of default for MGT-7 and AOC-4 late filing."},
    {"query": "What is the DIN requirement for company directors?",
     "domain": "mca",
     "ground_truth": "Every company director must have a Director Identification Number (DIN) obtained from MCA. KYC (DIR-3) annual renewal required."},
    {"query": "What is the minimum paid-up capital for a private limited company?",
     "domain": "mca",
     "ground_truth": "No minimum paid-up capital requirement for private limited companies after Companies Act 2013 amendment."},
    {"query": "What are AGM requirements for private limited companies?",
     "domain": "mca",
     "ground_truth": "First AGM within 9 months of financial year end. Subsequent AGMs within 6 months of financial year end. Gap between two AGMs max 15 months."},
]


def run_ragas_evaluation(test_cases: list[dict] = None) -> dict:
    """
    Run RAGAS evaluation on the golden test set.
    Returns scores for 4 metrics.
    """
    try:
        from ragas import evaluate
        from ragas.metrics import (
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall,
        )
        from datasets import Dataset
    except ImportError:
        print("RAGAS not installed. Run: pip install ragas datasets")
        return {}

    if test_cases is None:
        test_cases = GOLDEN_TEST_SET

    print(f"Running RAGAS evaluation on {len(test_cases)} test questions...")
    print(f"This calls the live agent pipeline — takes ~{len(test_cases) * 5} seconds\n")

    ragas_rows: list[dict] = []

    for i, tc in enumerate(test_cases, 1):
        print(f"  [{i}/{len(test_cases)}] {tc['query'][:60]}...")
        try:
            result = run_pipeline(query=tc["query"], domain=tc["domain"])
            answer_dict = result.get("answer", {})
            final_answer = answer_dict.get("final_answer", "")

            # Gather retrieved contexts
            contexts = []
            if answer_dict.get("source_url"):
                contexts.append(f"Source: {answer_dict['source_url']}")
            if answer_dict.get("circular_number"):
                contexts.append(f"Circular: {answer_dict['circular_number']}")

            ragas_rows.append({
                "question": tc["query"],
                "answer": final_answer,
                "contexts": contexts if contexts else ["No context retrieved"],
                "ground_truth": tc["ground_truth"],
            })
        except Exception as e:
            print(f"    Error: {e}")
            ragas_rows.append({
                "question": tc["query"],
                "answer": "Error",
                "contexts": ["Error"],
                "ground_truth": tc["ground_truth"],
            })

    # Build RAGAS dataset
    dataset = Dataset.from_list(ragas_rows)

    print("\nCalculating RAGAS scores...")
    results = evaluate(
        dataset=dataset,
        metrics=[
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall,
        ],
    )

    scores = {
        "faithfulness":      float(results["faithfulness"]),
        "answer_relevancy":  float(results["answer_relevancy"]),
        "context_precision": float(results["context_precision"]),
        "context_recall":    float(results["context_recall"]),
    }

    # Check against thresholds from config.py
    thresholds = {
        "faithfulness":      RAGAS_FAITHFULNESS_THRESHOLD,
        "answer_relevancy":  RAGAS_ANSWER_RELEVANCY_THRESHOLD,
        "context_precision": RAGAS_CONTEXT_PRECISION_THRESHOLD,
        "context_recall":    RAGAS_CONTEXT_RECALL_THRESHOLD,
    }

    print("\n" + "=" * 50)
    print("RAGAS EVALUATION RESULTS")
    print("=" * 50)
    all_pass = True
    for metric, score in scores.items():
        threshold = thresholds[metric]
        status = "✓ PASS" if score >= threshold else "✗ FAIL"
        if score < threshold:
            all_pass = False
        print(f"  {metric:25s} {score:.3f} (threshold {threshold}) {status}")

    print("=" * 50)
    print(f"  Overall: {'✓ ALL PASS' if all_pass else '✗ SOME METRICS BELOW THRESHOLD'}")
    print("=" * 50)
    print(f"\nRAG_TOP_K used: {RAG_TOP_K}")

    return scores


if __name__ == "__main__":
    run_ragas_evaluation()