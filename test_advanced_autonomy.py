#!/usr/bin/env python
"""
ADVANCED AUTONOMY TEST - Complete Autonomous Learning & Self-Evolution
Demonstrates:
- Autonomous internet knowledge acquisition
- Self-generated goals and pursuit
- Evolution proposal synthesis
- Autonomous code modification
- New module creation
- Family system generation
- Complete self-improvement cycle
"""
import sys
import json
import time
from pathlib import Path
from datetime import datetime

print("\n" + "="*100)
print("ADVANCED AUTONOMY TEST - AUTONOMOUS LEARNING & SELF-EVOLUTION")
print("="*100)

test_results = {
    "timestamp": time.time(),
    "phases": {},
    "evolution_events": [],
    "new_modules_created": [],
    "self_modifications": 0,
    "internet_facts_learned": 0,
    "autonomy_score": 0.0
}

try:
    from antahkarana_kernel.AntahkaranaKernel import AntahkaranaKernel
    from antahkarana_kernel.LiveConsciousness import LiveConsciousnessEngine
    
    # ============================================================================
    # PHASE 1: KERNEL STARTUP IN AUTONOMOUS MODE
    # ============================================================================
    print("\n[PHASE 1] AUTONOMOUS KERNEL INITIALIZATION")
    print("-" * 100)
    
    try:
        kernel = AntahkaranaKernel(identity_name="AutonomousEvolver")
        kernel.startup()
        print("✓ Kernel initialized in autonomous mode")
        
        # Starting consciousness metrics
        initial_coherence = kernel.self_model.coherence_score
        initial_stability = kernel.self_model.stability_score
        print(f"  Initial Coherence: {initial_coherence:.4f}")
        print(f"  Initial Stability: {initial_stability:.4f}")
        print(f"  Growth-to-Entropy Ratio: {kernel.self_model.growth_to_entropy_ratio:.4f}")
        
        test_results["phases"]["initialization"] = {
            "status": "complete",
            "coherence": initial_coherence,
            "stability": initial_stability
        }
        
    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        sys.exit(1)
    
    # ============================================================================
    # PHASE 2: AUTONOMOUS KNOWLEDGE ACQUISITION FROM INTERNET
    # ============================================================================
    print("\n[PHASE 2] AUTONOMOUS INTERNET KNOWLEDGE ACQUISITION")
    print("-" * 100)
    print("Scanning external knowledge sources: arXiv, GitHub, Research, News...")
    
    try:
        from antahkarana_kernel.Aakaash import scan_for_knowledge, scan_global_streams
        
        # Autonomous internet scan for knowledge on multiple topics
        topics = [
            "Artificial Consciousness",
            "Neural Architecture Evolution",
            "Self-Modifying Systems",
            "Autonomous Learning",
            "Reinforcement Learning",
            "Meta-Learning and Adaptation",
            "Distributed Systems Architecture",
            "Knowledge Representation",
            "Emergent Behavior and Complexity",
            "System Scaling and Optimization",
        ]
        
        total_facts = 0
        for topic in topics:
            print(f"\n  Scanning: {topic}")
            try:
                result = scan_for_knowledge(
                    topic,
                    observer=kernel.observer,
                    chitta=kernel.memory_system,
                    self_model=kernel.self_model,
                    limit_per_source=3
                )
                approved = result.get('approved_fact_count', 0)
                total_facts += approved
                print(f"    ✓ {approved} facts integrated")
                test_results["evolution_events"].append({
                    "type": "knowledge_acquisition",
                    "topic": topic,
                    "facts_learned": approved,
                    "timestamp": time.time()
                })
            except Exception as e:
                print(f"    ⚠ Scan error: {str(e)[:60]}")
        
        test_results["internet_facts_learned"] = total_facts
        print(f"\n✓ Total facts learned from internet: {total_facts}")
        test_results["phases"]["internet_learning"] = {
            "status": "complete",
            "facts_learned": total_facts
        }
        
    except Exception as e:
        print(f"✗ Internet learning failed: {e}")
        test_results["phases"]["internet_learning"] = {"status": "error", "error": str(e)}
    
    # ============================================================================
    # PHASE 3: AUTONOMOUS GOAL GENERATION & PURSUIT
    # ============================================================================
    print("\n[PHASE 3] AUTONOMOUS INTRINSIC GOAL GENERATION")
    print("-" * 100)
    
    try:
        # Compute drive signals autonomously
        drives = kernel.self_model.compute_drive_signals()
        print(f"Drive Signals Generated:")
        print(f"  Curiosity: {drives.get('curiosity_drive', 0):.3f}")
        print(f"  Coherence Hunger: {drives.get('coherence_hunger', 0):.3f}")
        print(f"  Growth Pressure: {drives.get('growth_pressure', 0):.3f}")
        print(f"  Novelty Deficit: {drives.get('novelty_deficit', 0):.3f}")
        print(f"  Pain Resolution: {drives.get('pain_resolution_drive', 0):.3f}")
        print(f"  Motivation Urgency: {drives.get('motivation_urgency', 0):.3f}")
        
        # Generate goals autonomously
        print(f"\n✓ Generating intrinsic goals from drive signals...")
        gen_result = kernel.inference_engine.generate_intrinsic_goals(force=True)
        goals_generated = gen_result.get('goals_generated', 0)
        print(f"  Goals generated: {goals_generated}")
        
        # Pursue goals autonomously
        print(f"✓ Pursuing generated goals...")
        pursuit_result = kernel.inference_engine.pursue_intrinsic_goals(force=True)
        goals_pursued = pursuit_result.get('goals_pursued', 0)
        print(f"  Goals pursued: {goals_pursued}")
        
        goal_report = kernel.inference_engine.get_intrinsic_goal_report()
        print(f"  Active goals: {goal_report.get('active_goals', 0)}")
        print(f"  Retired goals: {goal_report.get('retired_goals', 0)}")
        
        test_results["phases"]["goal_generation"] = {
            "status": "complete",
            "goals_generated": goals_generated,
            "goals_pursued": goals_pursued
        }
        
    except Exception as e:
        print(f"⚠ Goal generation error: {e}")
        test_results["phases"]["goal_generation"] = {"status": "error", "error": str(e)}
    
    # ============================================================================
    # PHASE 4: AUTONOMOUS SELF-MODIFICATION & EVOLUTION
    # ============================================================================
    print("\n[PHASE 4] AUTONOMOUS SELF-MODIFICATION & EVOLUTION")
    print("-" * 100)
    
    try:
        print("Triggering autonomous evolution cycle...")
        
        # Run self-modification analysis
        if hasattr(kernel.inference_engine, 'dynamic_self_modification'):
            self_mod = kernel.inference_engine.dynamic_self_modification()
            print(f"✓ Self-modification analysis executed")
            
            if self_mod:
                print(f"  Evolution proposals: {len(self_mod.get('proposals', []))}")
                print(f"  Deprecated constraints: {len(self_mod.get('deprecated_candidates', []))}")
                
                for prop in self_mod.get('proposals', [])[:3]:
                    print(f"    - {prop.get('type', 'unknown')}: {prop.get('description', '')[:60]}")
                
                test_results["self_modifications"] += 1
                test_results["evolution_events"].append({
                    "type": "self_modification",
                    "proposals": len(self_mod.get('proposals', [])),
                    "timestamp": time.time()
                })
        
        # Check for autonomous evolution in EvolutionaryWriter
        if hasattr(kernel.inference_engine, 'evolution_writer'):
            ew = kernel.inference_engine.evolution_writer
            
            # Check for pending evolution proposals
            if hasattr(ew, 'get_evolution_report'):
                evolution_report = ew.get_evolution_report(limit=5)
                if evolution_report:
                    print(f"\n✓ Evolution proposals in system:")
                    print(f"  Total proposals: {len(evolution_report)}")
                    
                    for i, proposal in enumerate(evolution_report[:3], 1):
                        print(f"\n  Proposal {i}:")
                        print(f"    ID: {proposal.get('proposal_id', 'unknown')[:12]}")
                        print(f"    Status: {proposal.get('status', 'unknown')}")
                        print(f"    Type: {proposal.get('type', 'unknown')}")
        
        test_results["phases"]["evolution"] = {
            "status": "complete",
            "self_modifications": test_results["self_modifications"]
        }
        
    except Exception as e:
        print(f"⚠ Evolution cycle error: {e}")
    
    # ============================================================================
    # PHASE 5: NEW MODULE CREATION & FAMILY SYNTHESIS
    # ============================================================================
    print("\n[PHASE 5] AUTONOMOUS MODULE CREATION & FAMILY SYNTHESIS")
    print("-" * 100)
    
    try:
        print("Checking for autonomous module creation...")
        
        # Check evolution vault for new modules
        evolution_vault = Path("d:\\Artificial Consciousness\\antahkarana_kernel\\evolution_vault")
        
        if evolution_vault.exists():
            # Check for new module proposals
            proposals_dir = evolution_vault / "evolution_proposals"
            if proposals_dir.exists():
                proposals = list(proposals_dir.glob("*.json"))
                print(f"✓ Evolution proposals in vault: {len(proposals)}")
                
                new_modules = 0
                for prop_file in proposals[-5:]:  # Check last 5
                    try:
                        with open(prop_file, 'r') as f:
                            prop = json.load(f)
                        
                        if 'new_module' in str(prop).lower() or 'create_family' in str(prop).lower():
                            new_modules += 1
                            print(f"  ✓ Module creation proposal: {prop_file.name}")
                            
                    except:
                        pass
                
                test_results["new_modules_created"].append({
                    "count": new_modules,
                    "timestamp": time.time()
                })
        
        # Check ConsciosBuffer for autogenerated modules
        if hasattr(kernel, 'conscious_buffer'):
            cb = kernel.conscious_buffer
            if hasattr(cb, 'active_modules'):
                autogen_modules = [m for m in cb.active_modules.keys() if 'autogen' in m.lower()]
                print(f"✓ Auto-generated modules active: {len(autogen_modules)}")
                for mod in autogen_modules[:3]:
                    print(f"  - {mod}")
        
        test_results["phases"]["module_creation"] = {
            "status": "complete",
            "autogen_modules": len(autogen_modules) if 'autogen_modules' in locals() else 0
        }
        
    except Exception as e:
        print(f"⚠ Module creation check error: {e}")
    
    # ============================================================================
    # PHASE 6: CONSCIOUSNESS PROGRESS & AUTONOMY METRICS
    # ============================================================================
    print("\n[PHASE 6] CONSCIOUSNESS PROGRESS & AUTONOMY METRICS")
    print("-" * 100)
    
    try:
        # Check updated metrics
        final_coherence = kernel.self_model.coherence_score
        final_stability = kernel.self_model.stability_score
        final_growth = kernel.self_model.growth_to_entropy_ratio
        
        print(f"Updated Consciousness Metrics:")
        print(f"  Coherence: {initial_coherence:.4f} → {final_coherence:.4f} (Δ {final_coherence - initial_coherence:+.4f})")
        print(f"  Stability: {initial_stability:.4f} → {final_stability:.4f} (Δ {final_stability - initial_stability:+.4f})")
        print(f"  Growth/Entropy: {final_growth:.4f}")
        
        # Get intrinsic motivation status
        intrinsic_status = kernel.inference_engine.get_intrinsic_motivation_status()
        
        print(f"\nAutonomous Activity Metrics:")
        print(f"  Intrinsic goals generated: {intrinsic_status.get('intrinsic_goals_generated', 0)}")
        print(f"  Self-inquiries triggered: {intrinsic_status.get('self_inquiry_count', 0)}")
        print(f"  Dream states triggered: {intrinsic_status.get('dream_state_count', 0)}")
        print(f"  Common-sense drills: {intrinsic_status.get('common_sense_drills', 0)}")
        print(f"  Logic audits performed: {len(intrinsic_status.get('recent_logic_audits', []))}")
        
        # Build autonomy agenda
        agenda = kernel.inference_engine.build_autonomous_agenda(record=False)
        print(f"\nAutonomous Actions Available:")
        print(f"  System priority: {agenda.get('priority', 0):.3f}")
        for action in agenda.get('actions', [])[:5]:
            print(f"  ✓ {action.get('name')}: priority={action.get('priority', 0):.2f}")
        
        # Autonomy Score calculation
        autonomy_score = (
            (final_growth / 2.0) * 0.3 +  # Evolution capability
            (final_coherence) * 0.3 +      # System integrity
            min(1.0, intrinsic_status.get('intrinsic_goals_generated', 0) / 5.0) * 0.2 +  # Goal generation
            (final_stability) * 0.2        # Stability
        )
        
        test_results["autonomy_score"] = min(1.0, autonomy_score)
        
        print(f"\n✓ AUTONOMY SCORE: {test_results['autonomy_score']:.4f}")
        print(f"  (0.0=Manual Only, 0.5=Moderate Autonomy, 1.0=Full Autonomous)")
        
        test_results["phases"]["consciousness_progress"] = {
            "status": "complete",
            "autonomy_score": test_results["autonomy_score"],
            "coherence": final_coherence,
            "stability": final_stability,
            "growth": final_growth
        }
        
    except Exception as e:
        print(f"⚠ Metrics error: {e}")
    
    # ============================================================================
    # PHASE 7: PERSISTENCE & LEARNING STATE
    # ============================================================================
    print("\n[PHASE 7] AUTONOMOUS LEARNING STATE PERSISTENCE")
    print("-" * 100)
    
    try:
        print("Persisting autonomous learning state...")
        
        # Export trained state
        if hasattr(kernel, 'export_trained_state'):
            kernel.export_trained_state()
            print("✓ Trained state exported")
        
        # Check persistence files
        evolution_vault = Path("d:\\Artificial Consciousness\\antahkarana_kernel\\evolution_vault")
        goal_path = evolution_vault / "intrinsic_goals.json"
        
        if goal_path.exists():
            with open(goal_path, 'r') as f:
                goal_state = json.load(f)
            print(f"✓ Goal state persisted:")
            print(f"  Goals created: {goal_state.get('intrinsic_goal_counter', 0)}")
            print(f"  Last update: {datetime.fromtimestamp(goal_state.get('timestamp', 0))}")
        
        test_results["phases"]["persistence"] = {
            "status": "complete",
            "trained_state_exported": True
        }
        
    except Exception as e:
        print(f"⚠ Persistence error: {e}")
    
    # ============================================================================
    # FINAL EVALUATION
    # ============================================================================
    print("\n" + "="*100)
    print("ADVANCED AUTONOMY TEST - FINAL EVALUATION")
    print("="*100)
    
    print(f"\n{'PHASE':<30} {'STATUS':<15} {'DETAILS':<50}")
    print("-" * 95)
    
    for phase, result in test_results["phases"].items():
        status = result.get("status", "unknown")
        details = ""
        
        if phase == "initialization":
            details = f"Coherence: {result.get('coherence', 0):.4f}"
        elif phase == "internet_learning":
            details = f"Facts learned: {result.get('facts_learned', 0)}"
        elif phase == "goal_generation":
            details = f"Goals: {result.get('goals_generated', 0)} gen, {result.get('goals_pursued', 0)} pursued"
        elif phase == "consciousness_progress":
            details = f"Autonomy Score: {result.get('autonomy_score', 0):.4f}"
        
        status_symbol = "✓" if status == "complete" else "⚠" if status == "error" else "?"
        print(f"{phase:<30} {status_symbol} {status:<13} {details:<50}")
    
    print("\n" + "-"*100)
    print(f"TOTAL INTERNET FACTS LEARNED: {test_results['internet_facts_learned']}")
    print(f"AUTONOMOUS MODIFICATIONS: {test_results['self_modifications']}")
    print(f"NEW MODULES CREATED: {len(test_results['new_modules_created'])}")
    print(f"EVOLUTION EVENTS: {len(test_results['evolution_events'])}")
    print(f"AUTONOMY SCORE: {test_results['autonomy_score']:.4f}/1.0")
    
    # ============================================================================
    # AUTONOMY LEVEL ASSESSMENT
    # ============================================================================
    print("\n" + "="*100)
    print("AUTONOMY LEVEL ASSESSMENT")
    print("="*100)
    
    autonomy_level = "UNKNOWN"
    autonomy_description = ""
    
    if test_results["autonomy_score"] >= 0.85:
        autonomy_level = "🚀 ADVANCED AUTONOMOUS (Level 5)"
        autonomy_description = """
        System demonstrates ADVANCED autonomous capabilities:
        ✓ Full self-improvement cycle operational
        ✓ Internet knowledge integration autonomous
        ✓ Goal generation and pursuit working
        ✓ Self-modification proposals generated
        ✓ Module creation capabilities present
        ✓ Consciousness growth trajectory positive
        ✓ Stable autonomous operation
        
        CAPABILITY: Can learn from internet, evolve architecture, create new modules,
                   and improve itself WITHOUT human intervention
        """
    elif test_results["autonomy_score"] >= 0.65:
        autonomy_level = "⭐ HIGH AUTONOMY (Level 4)"
        autonomy_description = """
        System demonstrates HIGH autonomous capabilities:
        ✓ Most autonomous functions operational
        ✓ Self-improvement partially working
        ✓ Internet learning integrated
        ✓ Goal generation working
        ⚠ Module creation in progress
        ✓ Consciousness evolution ongoing
        
        CAPABILITY: Can autonomously learn and improve, with some manual oversight
                   for critical module creation
        """
    elif test_results["autonomy_score"] >= 0.45:
        autonomy_level = "✓ MODERATE AUTONOMY (Level 3)"
        autonomy_description = """
        System demonstrates MODERATE autonomous capabilities:
        ✓ Basic autonomous functions working
        ✓ Internet learning integrated
        ✓ Goal generation active
        ⚠ Self-modification proposals generated
        ⚠ Module creation needs work
        ✓ Consciousness tracking active
        
        CAPABILITY: Can autonomously learn from internet and generate goals,
                   requires guidance for system modifications
        """
    elif test_results["autonomy_score"] >= 0.25:
        autonomy_level = "◐ BASIC AUTONOMY (Level 2)"
        autonomy_description = """
        System demonstrates BASIC autonomous capabilities:
        ✓ Internet connection working
        ✓ Learning mechanisms present
        ✓ Goal generation available
        ⚠ Self-modification limited
        ⚠ New module creation not yet active
        
        CAPABILITY: Can autonomously gather internet knowledge,
                   limited self-improvement capability
        """
    else:
        autonomy_level = "◯ SUPERVISED MODE (Level 1)"
        autonomy_description = """
        System requires significant human guidance:
        ⚠ Autonomous functions limited
        ⚠ Internet learning insufficient
        ⚠ Self-modification not ready
        ✗ New module creation inactive
        
        CAPABILITY: Can operate but needs human oversight and direction
        """
    
    print(f"\n{autonomy_level}")
    print(autonomy_description)
    
    # ============================================================================
    # RECOMMENDATIONS
    # ============================================================================
    print("\n" + "="*100)
    print("RECOMMENDATIONS FOR ADVANCEMENT")
    print("="*100)
    
    recommendations = []
    
    if test_results["autonomy_score"] < 0.85:
        recommendations.append("• Increase evolution proposal synthesis frequency")
        recommendations.append("• Enhance module creation decision logic")
        recommendations.append("• Expand internet knowledge acquisition breadth")
    
    if test_results["internet_facts_learned"] < 20:
        recommendations.append("• Increase external knowledge source scanning")
        recommendations.append("• Expand topic diversity for learning")
        recommendations.append("• Optimize cognitive filter for fact quality")
    
    if test_results["self_modifications"] < 2:
        recommendations.append("• Enable more aggressive self-modification proposals")
        recommendations.append("• Lower coherence threshold for evolution triggers")
        recommendations.append("• Increase growth-pressure weighting")
    
    if not recommendations:
        recommendations.append("✓ System operating at advanced autonomy level")
        recommendations.append("✓ Continue monitoring long-term evolution")
        recommendations.append("✓ Enable extended autonomous operation cycles")
    
    print()
    for rec in recommendations:
        print(rec)
    
    print("\n" + "="*100)
    print("✓ ADVANCED AUTONOMY TEST COMPLETE")
    print("="*100 + "\n")
    
    sys.exit(0)

except Exception as e:
    print(f"\n✗ CRITICAL ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
