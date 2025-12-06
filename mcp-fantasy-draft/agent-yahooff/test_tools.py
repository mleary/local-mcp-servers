#!/usr/bin/env python
"""
Quick test script to verify the Yahoo Fantasy Football agent tools work.
Run this to test without needing Copilot CLI setup.
"""

import json
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from server import get_my_team_roster, get_drafted_players, search_available_players


def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def test_roster():
    print_section("Testing: Get My Team Roster")
    try:
        result = get_my_team_roster()
        data = json.loads(result)
        
        if "error" in data:
            print(f"❌ Error: {data['error']}")
            return False
        
        print(f"✅ Found {len(data)} players on your roster")
        print("\nFirst 3 players:")
        for player in data[:3]:
            print(f"  - {player['name']} ({', '.join(player['eligible_positions'])})")
        return True
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def test_drafted_players():
    print_section("Testing: Get Drafted Players")
    try:
        result = get_drafted_players()
        data = json.loads(result)
        
        if "error" in data:
            print(f"❌ Error: {data['error']}")
            return False
        
        print(f"✅ Found {len(data)} drafted players in league")
        print("\nFirst 3 drafted players:")
        for player in data[:3]:
            ownership = player.get('percent_owned', 'N/A')
            print(f"  - {player['name']} ({', '.join(player['eligible_positions'])}) - {ownership}% owned")
        return True
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def test_available_players():
    print_section("Testing: Search Available Players (QBs)")
    try:
        result = search_available_players(position="QB", limit=5)
        data = json.loads(result)
        
        if "error" in data:
            print(f"❌ Error: {data['error']}")
            return False
        
        print(f"✅ Found {len(data)} available QBs")
        print("\nTop 5 available QBs:")
        for player in data:
            ownership = player.get('percent_owned', 'N/A')
            status = player.get('status', '')
            status_str = f" [{status}]" if status else ""
            print(f"  - {player['name']} - {ownership}% owned{status_str}")
        return True
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def main():
    print("\n" + "="*60)
    print("  Yahoo Fantasy Football Agent - Tool Tests")
    print("="*60)
    print("\nThis will test all three agent tools...")
    
    results = []
    
    # Test each tool
    results.append(("Get My Team Roster", test_roster()))
    results.append(("Get Drafted Players", test_drafted_players()))
    results.append(("Search Available Players", test_available_players()))
    
    # Summary
    print_section("Test Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tools working! Agent is ready to use.")
        return 0
    else:
        print("\n⚠️  Some tools failed. Check configuration and OAuth.")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        sys.exit(1)
