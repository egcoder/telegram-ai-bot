#!/usr/bin/env python3
"""
Performance and Load Tests for Telegram AI Bot

This script tests the bot's performance under various load conditions
and measures response times for different operations.
"""
import os
import sys
import time
import asyncio
import statistics
import tempfile
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from concurrent.futures import ThreadPoolExecutor

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from telegram_ai_bot.utils.user_manager import UserManager
from telegram_ai_bot.utils.calendar_utils import generate_calendar_link, parse_deadline
from telegram_ai_bot.utils.ai_service import AIService

class PerformanceTest:
    """Performance testing class"""
    
    def __init__(self):
        self.temp_dir = None
        self.results = {}
        
    def setup(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock environment
        os.environ.update({
            'TELEGRAM_BOT_TOKEN': '123456789:test_token',
            'OPENAI_API_KEY': 'test_key',
            'ADMIN_USER_ID': '123456789'
        })
        
    def cleanup(self):
        """Clean up test environment"""
        if self.temp_dir:
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            
    def measure_time(self, func, *args, **kwargs):
        """Measure execution time of a function"""
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        return result, end_time - start_time
        
    async def measure_time_async(self, coro):
        """Measure execution time of an async function"""
        start_time = time.time()
        result = await coro
        end_time = time.time()
        return result, end_time - start_time
        
    def test_user_manager_performance(self, num_users=1000):
        """Test user manager performance with many users"""
        print(f"🔍 Testing UserManager performance with {num_users} users...")
        
        users_file = Path(self.temp_dir) / 'test_users.json'
        user_manager = UserManager(users_file)
        
        # Test adding users
        add_times = []
        for i in range(num_users):
            _, duration = self.measure_time(user_manager.add_user, i)
            add_times.append(duration)
            
        # Test checking authorization
        check_times = []
        for i in range(0, num_users, 10):  # Check every 10th user
            _, duration = self.measure_time(user_manager.is_authorized, i)
            check_times.append(duration)
            
        # Test removing users
        remove_times = []
        for i in range(0, num_users, 100):  # Remove every 100th user
            _, duration = self.measure_time(user_manager.remove_user, i)
            remove_times.append(duration)
            
        self.results['user_manager'] = {
            'add_avg_time': statistics.mean(add_times),
            'add_max_time': max(add_times),
            'check_avg_time': statistics.mean(check_times),
            'check_max_time': max(check_times),
            'remove_avg_time': statistics.mean(remove_times),
            'remove_max_time': max(remove_times),
            'num_users': num_users
        }
        
        print(f"  ✅ Add user avg: {statistics.mean(add_times)*1000:.2f}ms")
        print(f"  ✅ Check auth avg: {statistics.mean(check_times)*1000:.2f}ms")
        print(f"  ✅ Remove user avg: {statistics.mean(remove_times)*1000:.2f}ms")
        
    def test_calendar_utils_performance(self, num_operations=1000):
        """Test calendar utilities performance"""
        print(f"📅 Testing calendar utilities performance with {num_operations} operations...")
        
        # Test calendar link generation
        link_times = []
        for i in range(num_operations):
            _, duration = self.measure_time(
                generate_calendar_link,
                f"Test Event {i}",
                f"Test description {i}"
            )
            link_times.append(duration)
            
        # Test deadline parsing
        deadline_texts = [
            "tomorrow at 3 PM",
            "next week",
            "today at 9 AM",
            "next month",
            "meeting at 14:30"
        ]
        
        parse_times = []
        for i in range(num_operations):
            text = deadline_texts[i % len(deadline_texts)]
            _, duration = self.measure_time(parse_deadline, text)
            parse_times.append(duration)
            
        self.results['calendar_utils'] = {
            'link_gen_avg_time': statistics.mean(link_times),
            'link_gen_max_time': max(link_times),
            'deadline_parse_avg_time': statistics.mean(parse_times),
            'deadline_parse_max_time': max(parse_times),
            'num_operations': num_operations
        }
        
        print(f"  ✅ Calendar link gen avg: {statistics.mean(link_times)*1000:.2f}ms")
        print(f"  ✅ Deadline parse avg: {statistics.mean(parse_times)*1000:.2f}ms")
        
    async def test_ai_service_performance(self, num_requests=50):
        """Test AI service performance (mocked)"""
        print(f"🤖 Testing AI service performance with {num_requests} requests...")
        
        with patch('telegram_ai_bot.utils.ai_service.OpenAI') as mock_openai:
            # Mock client responses
            mock_client = Mock()
            mock_openai.return_value = mock_client
            
            # Mock transcription response
            mock_client.audio.transcriptions.create.return_value = "Test transcription"
            
            # Mock analysis response  
            mock_response = Mock()
            mock_choice = Mock()
            mock_message = Mock()
            mock_message.content = '{"summary": "test", "action_items": [], "topics": []}'
            mock_choice.message = mock_message
            mock_response.choices = [mock_choice]
            mock_client.chat.completions.create.return_value = mock_response
            
            service = AIService("test_key")
            
            # Test transcription performance
            transcribe_times = []
            for i in range(num_requests):
                # Create mock audio file
                with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as f:
                    f.write(b"fake audio data")
                    audio_path = Path(f.name)
                    
                try:
                    _, duration = await self.measure_time_async(
                        service.transcribe_audio(audio_path)
                    )
                    transcribe_times.append(duration)
                finally:
                    audio_path.unlink()
                    
            # Test analysis performance
            analysis_times = []
            for i in range(num_requests):
                _, duration = await self.measure_time_async(
                    service.analyze_text(f"Test content {i}", "TestUser")
                )
                analysis_times.append(duration)
                
            self.results['ai_service'] = {
                'transcribe_avg_time': statistics.mean(transcribe_times),
                'transcribe_max_time': max(transcribe_times),
                'analysis_avg_time': statistics.mean(analysis_times),
                'analysis_max_time': max(analysis_times),
                'num_requests': num_requests
            }
            
            print(f"  ✅ Transcription avg: {statistics.mean(transcribe_times)*1000:.2f}ms")
            print(f"  ✅ Analysis avg: {statistics.mean(analysis_times)*1000:.2f}ms")
            
    async def test_concurrent_operations(self, concurrent_users=10):
        """Test concurrent user operations"""
        print(f"⚡ Testing concurrent operations with {concurrent_users} users...")
        
        users_file = Path(self.temp_dir) / 'concurrent_users.json'
        user_manager = UserManager(users_file)
        
        async def simulate_user_session(user_id):
            """Simulate a user session"""
            start_time = time.time()
            
            # Add user
            user_manager.add_user(user_id)
            
            # Check authorization multiple times
            for _ in range(10):
                user_manager.is_authorized(user_id)
                
            # Generate calendar links
            for i in range(5):
                generate_calendar_link(f"Event {user_id}_{i}", f"Description {i}")
                
            end_time = time.time()
            return end_time - start_time
            
        # Run concurrent user sessions
        start_time = time.time()
        tasks = [simulate_user_session(i) for i in range(concurrent_users)]
        session_times = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        self.results['concurrent_ops'] = {
            'total_time': total_time,
            'avg_session_time': statistics.mean(session_times),
            'max_session_time': max(session_times),
            'concurrent_users': concurrent_users,
            'throughput': concurrent_users / total_time
        }
        
        print(f"  ✅ Total time: {total_time:.2f}s")
        print(f"  ✅ Avg session time: {statistics.mean(session_times):.2f}s")
        print(f"  ✅ Throughput: {concurrent_users/total_time:.2f} users/sec")
        
    def test_memory_usage(self):
        """Test memory usage with large datasets"""
        print("💾 Testing memory usage...")
        
        import psutil
        import gc
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create large user manager
        users_file = Path(self.temp_dir) / 'memory_test_users.json'
        user_manager = UserManager(users_file)
        
        # Add many users
        num_users = 10000
        for i in range(num_users):
            user_manager.add_user(i)
            
        mid_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Generate many calendar links
        links = []
        for i in range(1000):
            link = generate_calendar_link(f"Event {i}", f"Description {i}")
            links.append(link)
            
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Clean up
        del links
        del user_manager
        gc.collect()
        
        cleanup_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        self.results['memory_usage'] = {
            'initial_memory_mb': initial_memory,
            'mid_memory_mb': mid_memory,
            'final_memory_mb': final_memory,
            'cleanup_memory_mb': cleanup_memory,
            'peak_usage_mb': final_memory - initial_memory,
            'num_users': num_users
        }
        
        print(f"  ✅ Initial memory: {initial_memory:.1f}MB")
        print(f"  ✅ Peak memory: {final_memory:.1f}MB")
        print(f"  ✅ Memory increase: {final_memory - initial_memory:.1f}MB")
        print(f"  ✅ After cleanup: {cleanup_memory:.1f}MB")
        
    def print_performance_report(self):
        """Print comprehensive performance report"""
        print("\n" + "="*70)
        print("📊 TELEGRAM AI BOT - PERFORMANCE TEST REPORT")
        print("="*70)
        
        # User Manager Performance
        if 'user_manager' in self.results:
            um = self.results['user_manager']
            print(f"\n👤 USER MANAGER PERFORMANCE ({um['num_users']} users):")
            print(f"  Add User:      {um['add_avg_time']*1000:.2f}ms avg, {um['add_max_time']*1000:.2f}ms max")
            print(f"  Check Auth:    {um['check_avg_time']*1000:.2f}ms avg, {um['check_max_time']*1000:.2f}ms max")
            print(f"  Remove User:   {um['remove_avg_time']*1000:.2f}ms avg, {um['remove_max_time']*1000:.2f}ms max")
            
        # Calendar Utils Performance
        if 'calendar_utils' in self.results:
            cu = self.results['calendar_utils']
            print(f"\n📅 CALENDAR UTILS PERFORMANCE ({cu['num_operations']} operations):")
            print(f"  Link Gen:      {cu['link_gen_avg_time']*1000:.2f}ms avg, {cu['link_gen_max_time']*1000:.2f}ms max")
            print(f"  Parse Deadline:{cu['deadline_parse_avg_time']*1000:.2f}ms avg, {cu['deadline_parse_max_time']*1000:.2f}ms max")
            
        # AI Service Performance
        if 'ai_service' in self.results:
            ai = self.results['ai_service']
            print(f"\n🤖 AI SERVICE PERFORMANCE ({ai['num_requests']} requests):")
            print(f"  Transcription: {ai['transcribe_avg_time']*1000:.2f}ms avg, {ai['transcribe_max_time']*1000:.2f}ms max")
            print(f"  Analysis:      {ai['analysis_avg_time']*1000:.2f}ms avg, {ai['analysis_max_time']*1000:.2f}ms max")
            
        # Concurrent Operations
        if 'concurrent_ops' in self.results:
            co = self.results['concurrent_ops']
            print(f"\n⚡ CONCURRENT OPERATIONS ({co['concurrent_users']} users):")
            print(f"  Total Time:    {co['total_time']:.2f}s")
            print(f"  Avg Session:   {co['avg_session_time']:.2f}s")
            print(f"  Throughput:    {co['throughput']:.2f} users/sec")
            
        # Memory Usage
        if 'memory_usage' in self.results:
            mu = self.results['memory_usage']
            print(f"\n💾 MEMORY USAGE ({mu['num_users']} users):")
            print(f"  Initial:       {mu['initial_memory_mb']:.1f}MB")
            print(f"  Peak:          {mu['final_memory_mb']:.1f}MB")
            print(f"  Increase:      {mu['peak_usage_mb']:.1f}MB")
            print(f"  After Cleanup: {mu['cleanup_memory_mb']:.1f}MB")
            
        print("\n" + "="*70)
        print("📈 PERFORMANCE SUMMARY:")
        
        # Performance recommendations
        recommendations = []
        
        if 'user_manager' in self.results:
            um = self.results['user_manager']
            if um['add_avg_time'] > 0.001:  # > 1ms
                recommendations.append("⚠️  Consider database for user storage (>1ms add time)")
            if um['check_avg_time'] > 0.0001:  # > 0.1ms
                recommendations.append("⚠️  Consider caching for authorization checks")
                
        if 'concurrent_ops' in self.results:
            co = self.results['concurrent_ops']
            if co['throughput'] < 10:
                recommendations.append("⚠️  Low throughput - consider async optimizations")
                
        if 'memory_usage' in self.results:
            mu = self.results['memory_usage']
            if mu['peak_usage_mb'] > 100:
                recommendations.append("⚠️  High memory usage - consider optimization")
                
        if recommendations:
            print("\n🔧 RECOMMENDATIONS:")
            for rec in recommendations:
                print(f"  {rec}")
        else:
            print("✅ All performance metrics within acceptable ranges!")
            
        print("="*70)

async def main():
    """Main performance test execution"""
    print("🚀 Starting Telegram AI Bot Performance Tests...")
    
    tester = PerformanceTest()
    
    try:
        tester.setup()
        
        # Run performance tests
        tester.test_user_manager_performance(1000)
        tester.test_calendar_utils_performance(1000)
        await tester.test_ai_service_performance(50)
        await tester.test_concurrent_operations(10)
        tester.test_memory_usage()
        
        # Print comprehensive report
        tester.print_performance_report()
        
        return 0
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return 1
        
    finally:
        tester.cleanup()

if __name__ == "__main__":
    # Handle Python 3.13 compatibility
    if sys.version_info >= (3, 13):
        import warnings
        warnings.filterwarnings("ignore", category=DeprecationWarning)
    
    # Run performance tests
    exit_code = asyncio.run(main())
    sys.exit(exit_code)