"""
Unified RFP Automation Workflow
Integrates Sales-agent-main, Technichal_Agent-main, and pricing_agent according to architecture
"""
import sys
import json
from pathlib import Path
from typing import Dict, Any, List, TypedDict
from datetime import datetime

# Add paths for all three systems
sales_path = Path(__file__).parent / "Sales-agent-main"
tech_path = Path(__file__).parent / "Technichal_Agent-main"
pricing_path = Path(__file__).parent / "pricing_agent"

sys.path.insert(0, str(sales_path))
sys.path.insert(0, str(tech_path))
sys.path.insert(0, str(pricing_path))

# Import from Sales-agent-main
from agents.rfp_scraper import scrape_urls
from agents.sales_agent import filter_due_within, summarize_rfps, select_best_rfp
from agents.response_agent import generate_draft_response

# Import from pricing_agent
from pricing_agent import run_pricing_agent

# Import for spec matching
try:
    from query import search_cables
except ImportError:
    # Fallback if query.py not available
    def search_cables(query, top_k=5):
        return []

# LangGraph imports
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver


# Define the state for our unified workflow
class WorkflowState(TypedDict):
    """State that flows through the entire RFP processing pipeline"""
    # Input
    rfp_urls: List[str]
    
    # Stage 1: RFP Discovery (Sales Agent)
    all_rfps: List[Dict[str, Any]]
    filtered_rfps: List[Dict[str, Any]]
    summarized_rfps: List[Dict[str, Any]]
    selected_rfp: Dict[str, Any]
    
    # Stage 2: Spec Matching (Technical Agent)
    product_requirements: List[str]
    spec_matches: List[Dict[str, Any]]
    
    # Stage 3: Pricing (Pricing Agent)
    pricing_input: Dict[str, Any]
    pricing_result: Dict[str, Any]
    
    # Stage 4: Response Generation (Sales Agent)
    draft_response: str
    
    # Final output
    final_package: Dict[str, Any]
    
    # Status tracking
    current_stage: str
    errors: List[str]


class UnifiedRFPWorkflow:
    """
    Unified workflow that orchestrates all three agents:
    1. Sales Agent (RFP scraping, filtering, selection)
    2. Technical Spec-Match Agent (Product matching)
    3. Pricing Agent (Cost calculation)
    4. Response Generation (Final RFP response)
    """
    
    # RFP Sources
    DEFAULT_URLS = [
        "https://etenders.gov.in/eprocure/app",
        "https://tenders.gov.in",
        "https://gem.gov.in/tenders",
        "https://tenderwizard.com",
        "https://www.rfpdb.com",
        "https://www.findrfp.com",
        "https://www.globaltenders.com",
    ]
    
    def __init__(self):
        """Initialize the unified workflow with LangGraph"""
        self.workflow = StateGraph(WorkflowState)
        self._build_graph()
        self.app = None
    
    def _build_graph(self):
        """Build the LangGraph workflow according to architecture"""
        
        # Add all nodes
        self.workflow.add_node("scrape_rfps", self.scrape_rfps_node)
        self.workflow.add_node("filter_rfps", self.filter_rfps_node)
        self.workflow.add_node("summarize_rfps", self.summarize_rfps_node)
        self.workflow.add_node("select_best_rfp", self.select_best_rfp_node)
        self.workflow.add_node("spec_match", self.spec_match_node)
        self.workflow.add_node("calculate_pricing", self.pricing_node)
        self.workflow.add_node("generate_response", self.response_node)
        self.workflow.add_node("package_output", self.package_output_node)
        
        # Define the flow
        self.workflow.set_entry_point("scrape_rfps")
        self.workflow.add_edge("scrape_rfps", "filter_rfps")
        self.workflow.add_edge("filter_rfps", "summarize_rfps")
        self.workflow.add_edge("summarize_rfps", "select_best_rfp")
        self.workflow.add_edge("select_best_rfp", "spec_match")
        self.workflow.add_edge("spec_match", "calculate_pricing")
        self.workflow.add_edge("calculate_pricing", "generate_response")
        self.workflow.add_edge("generate_response", "package_output")
        self.workflow.add_edge("package_output", END)
        
        # Compile with memory
        memory = MemorySaver()
        self.app = self.workflow.compile(checkpointer=memory)
        
        print("✅ Unified workflow graph compiled successfully")
    
    # ==================== Node Implementations ====================
    
    def scrape_rfps_node(self, state: WorkflowState) -> WorkflowState:
        """Node 1: Scrape RFPs from sources"""
        print("\n🔍 Stage 1: Scraping RFPs from sources...")
        state["current_stage"] = "scraping"
        
        try:
            urls = state.get("rfp_urls", self.DEFAULT_URLS)
            rfps = scrape_urls(urls)
            state["all_rfps"] = rfps
            print(f"✅ Scraped {len(rfps)} RFPs")
        except Exception as e:
            print(f"❌ Scraping error: {e}")
            state["errors"].append(f"Scraping error: {e}")
            state["all_rfps"] = []
        
        return state
    
    def filter_rfps_node(self, state: WorkflowState) -> WorkflowState:
        """Node 2: Filter RFPs due within 90 days"""
        print("\n📅 Stage 2: Filtering RFPs...")
        state["current_stage"] = "filtering"
        
        try:
            all_rfps = state.get("all_rfps", [])
            filtered = filter_due_within(all_rfps, days=90)
            state["filtered_rfps"] = filtered
            print(f"✅ Filtered to {len(filtered)} candidates")
        except Exception as e:
            print(f"❌ Filtering error: {e}")
            state["errors"].append(f"Filtering error: {e}")
            state["filtered_rfps"] = state.get("all_rfps", [])
        
        return state
    
    def summarize_rfps_node(self, state: WorkflowState) -> WorkflowState:
        """Node 3: Summarize RFPs using LLM"""
        print("\n🧠 Stage 3: Summarizing RFPs...")
        state["current_stage"] = "summarizing"
        
        try:
            filtered = state.get("filtered_rfps", [])
            summarized = summarize_rfps(filtered)
            state["summarized_rfps"] = summarized
            print(f"✅ Summarized {len(summarized)} RFPs")
        except Exception as e:
            print(f"❌ Summarization error: {e}")
            state["errors"].append(f"Summarization error: {e}")
            # Fallback: use filtered RFPs without summaries
            state["summarized_rfps"] = state.get("filtered_rfps", [])
        
        return state
    
    def select_best_rfp_node(self, state: WorkflowState) -> WorkflowState:
        """Node 4: Select best RFP for response"""
        print("\n🎯 Stage 4: Selecting best RFP...")
        state["current_stage"] = "selection"
        
        try:
            summarized = state.get("summarized_rfps", [])
            if not summarized:
                raise ValueError("No RFPs available for selection")
            
            selected = select_best_rfp(summarized)
            state["selected_rfp"] = selected
            print(f"✅ Selected: {selected.get('title')}")
            print(f"   Due: {selected.get('due_date')}")
        except Exception as e:
            print(f"❌ Selection error: {e}")
            state["errors"].append(f"Selection error: {e}")
            # Fallback: select first RFP
            summarized = state.get("summarized_rfps", [])
            state["selected_rfp"] = summarized[0] if summarized else {}
        
        return state
    
    def spec_match_node(self, state: WorkflowState) -> WorkflowState:
        """Node 5: Match products from SKU repository (Cyan box - Spec-Match Task)"""
        print("\n🔧 Stage 5: Matching product specifications...")
        state["current_stage"] = "spec_matching"
        
        try:
            selected_rfp = state.get("selected_rfp", {})
            description = selected_rfp.get("description", "")
            
            # Extract product requirements from RFP description
            # For demo, we'll use some example queries
            queries = self._extract_product_requirements(description)
            state["product_requirements"] = queries
            
            # Search for matching products
            all_matches = []
            for query in queries[:5]:  # Limit to top 5 requirements
                print(f"  🔍 Searching: {query}")
                matches = search_cables(query, top_k=3)
                for score, record in matches:
                    all_matches.append({
                        "query": query,
                        "match_score": float(score),
                        "product": {
                            "conductor_area_mm2": record.get('conductor_nominal_area_mm2'),
                            "current_rating_amps": record.get('current_rating_amps'),
                            "diameter_mm": record.get('approx_overall_diameter_mm'),
                            "weight_kg_per_km": record.get('overall_weight_kg_per_km'),
                        },
                        "recommendation": f"{record.get('conductor_nominal_area_mm2')} sq mm cable, {record.get('current_rating_amps')} amps"
                    })
            
            state["spec_matches"] = all_matches
            print(f"✅ Found {len(all_matches)} product matches")
            
        except Exception as e:
            print(f"❌ Spec matching error: {e}")
            state["errors"].append(f"Spec matching error: {e}")
            state["spec_matches"] = []
        
        return state
    
    def pricing_node(self, state: WorkflowState) -> WorkflowState:
        """Node 6: Calculate pricing (Cyan box - Pricing Task)"""
        print("\n💰 Stage 6: Calculating pricing...")
        state["current_stage"] = "pricing"
        
        try:
            selected_rfp = state.get("selected_rfp", {})
            spec_matches = state.get("spec_matches", [])
            
            # Prepare pricing input
            technical_table = []
            for idx, match in enumerate(spec_matches, 1):
                technical_table.append({
                    "item_no": idx,
                    "description": match.get("recommendation", "Product"),
                    "specifications": match.get("product", {}),
                    "quantity": 1000,  # Default quantity
                    "match_score": match.get("match_score", 0.0)
                })
            
            pricing_input = {
                "rfp_id": selected_rfp.get("title", "Unknown"),
                "technical_table": technical_table,
                "rfp_summary": {
                    "tests": ["Quality Test", "Performance Test", "Safety Test"]
                }
            }
            
            state["pricing_input"] = pricing_input
            
            # Run pricing agent
            print("  📊 Running pricing calculations...")
            pricing_result = run_pricing_agent(pricing_input)
            state["pricing_result"] = pricing_result
            
            total = pricing_result.get("grand_total", 0)
            print(f"✅ Pricing calculated: ${total:,.2f}")
            
        except Exception as e:
            print(f"❌ Pricing error: {e}")
            state["errors"].append(f"Pricing error: {e}")
            # Fallback pricing
            state["pricing_result"] = {
                "total_material_cost": 50000,
                "total_test_cost": 5000,
                "grand_total": 55000,
                "note": "Estimated pricing"
            }
        
        return state
    
    def response_node(self, state: WorkflowState) -> WorkflowState:
        """Node 7: Generate RFP response draft"""
        print("\n✍️  Stage 7: Generating response draft...")
        state["current_stage"] = "response_generation"
        
        try:
            selected_rfp = state.get("selected_rfp", {})
            spec_matches = state.get("spec_matches", [])
            pricing_result = state.get("pricing_result", {})
            
            # Enhance RFP data with our results
            enhanced_rfp = {
                **selected_rfp,
                "spec_match_count": len(spec_matches),
                "total_cost": pricing_result.get("grand_total", 0)
            }
            
            # Generate response
            response = generate_draft_response(enhanced_rfp)
            state["draft_response"] = response
            print("✅ Response draft generated")
            
        except Exception as e:
            print(f"❌ Response generation error: {e}")
            state["errors"].append(f"Response generation error: {e}")
            state["draft_response"] = "Response generation failed"
        
        return state
    
    def package_output_node(self, state: WorkflowState) -> WorkflowState:
        """Node 8: Package final output"""
        print("\n📦 Stage 8: Packaging final output...")
        state["current_stage"] = "completed"
        
        selected_rfp = state.get("selected_rfp", {})
        
        final_package = {
            "rfp_details": {
                "title": selected_rfp.get("title"),
                "due_date": selected_rfp.get("due_date"),
                "source": selected_rfp.get("link"),
                "summary": selected_rfp.get("summary")
            },
            "spec_matches": {
                "count": len(state.get("spec_matches", [])),
                "products": state.get("spec_matches", [])
            },
            "pricing": state.get("pricing_result", {}),
            "draft_response": state.get("draft_response", ""),
            "processing_summary": {
                "total_rfps_scraped": len(state.get("all_rfps", [])),
                "candidates_found": len(state.get("filtered_rfps", [])),
                "products_matched": len(state.get("spec_matches", [])),
                "errors": state.get("errors", []),
                "generated_at": datetime.utcnow().isoformat()
            }
        }
        
        state["final_package"] = final_package
        
        # Save to file
        output_file = Path(__file__).parent / "rfp_final_response.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_package, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Final package saved to: {output_file}")
        print(f"\n🎉 Workflow completed successfully!")
        
        return state
    
    # ==================== Helper Methods ====================
    
    def _extract_product_requirements(self, description: str) -> List[str]:
        """Extract product requirements from RFP description"""
        # Simple keyword-based extraction (can be enhanced with NLP)
        keywords = ["cable", "wire", "conductor", "power", "electrical", "voltage"]
        
        queries = []
        description_lower = description.lower()
        
        if any(kw in description_lower for kw in keywords):
            queries.append("high current rating cables for industrial use")
            queries.append("1.5 sq mm to 10 sq mm electrical cables")
            queries.append("heavy duty power cables with insulation")
        else:
            queries.append("general purpose electrical cables")
        
        return queries if queries else ["electrical cables and wires"]
    
    # ==================== Main Execution ====================
    
    def run(self, rfp_urls: List[str] = None) -> Dict[str, Any]:
        """
        Run the complete unified workflow
        
        Args:
            rfp_urls: Optional list of RFP source URLs
            
        Returns:
            Final package with all results
        """
        print("\n" + "="*70)
        print("🚀 UNIFIED RFP AUTOMATION WORKFLOW")
        print("="*70)
        
        # Initialize state
        initial_state = {
            "rfp_urls": rfp_urls or self.DEFAULT_URLS,
            "all_rfps": [],
            "filtered_rfps": [],
            "summarized_rfps": [],
            "selected_rfp": {},
            "product_requirements": [],
            "spec_matches": [],
            "pricing_input": {},
            "pricing_result": {},
            "draft_response": "",
            "final_package": {},
            "current_stage": "initialized",
            "errors": []
        }
        
        # Run the workflow
        config = {"configurable": {"thread_id": f"rfp_{datetime.now().timestamp()}"}}
        final_state = self.app.invoke(initial_state, config)
        
        return final_state.get("final_package", {})


def main():
    """Main entry point"""
    # Create and run workflow
    workflow = UnifiedRFPWorkflow()
    result = workflow.run()
    
    # Display summary
    print("\n" + "="*70)
    print("📊 WORKFLOW SUMMARY")
    print("="*70)
    print(f"RFP Title: {result.get('rfp_details', {}).get('title')}")
    print(f"Products Matched: {result.get('spec_matches', {}).get('count')}")
    print(f"Total Cost: ${result.get('pricing', {}).get('grand_total', 0):,.2f}")
    print(f"Response Generated: {'Yes' if result.get('draft_response') else 'No'}")
    print("="*70)


if __name__ == "__main__":
    main()

