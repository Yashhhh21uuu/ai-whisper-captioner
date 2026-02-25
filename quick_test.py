from grammar_corrected_captioner import GrammarCorrectedCaptioner

def test_grammar_correction():
    """Test the grammar correction on sample text"""
    captioner = GrammarCorrectedCaptioner(model_size="base")
    
    # Test cases with common errors
    test_sentences = [
        "i am going to the store their going to meet us",
        "your welcome to the meeting its starting now",
        "she done good on the test effecting her grade",
        "we should of went there earlier then planned"
    ]
    
    print("🧪 Testing Grammar Correction:")
    print("=" * 50)
    
    for sentence in test_sentences:
        corrected = captioner.enhance_transcription(sentence)
        print(f"Original:  {sentence}")
        print(f"Corrected: {corrected}")
        print("-" * 30)

if __name__ == "__main__":
    test_grammar_correction()