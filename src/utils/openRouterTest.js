/**
 * OpenRouter Proxy Test Utility
 * Tests the deployed Google Cloud Function proxy to ensure it's working correctly
 */

class OpenRouterTester {
  constructor() {
    this.baseUrl = 'https://openrouter-proxy-456775528821.europe-west1.run.app/';
    this.model = 'google/gemini-2.5-pro';
    this.temperature = 0.7;
  }

  /**
   * Simple connectivity test
   */
  async testConnectivity() {
    console.log('🔗 Testing OpenRouter proxy connectivity...');
    
    try {
      const response = await fetch(this.baseUrl, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      console.log(`📡 Response status: ${response.status}`);
      console.log(`📡 Response headers:`, Object.fromEntries(response.headers.entries()));
      
      if (response.ok) {
        console.log('✅ Proxy endpoint is reachable');
        return true;
      } else {
        console.log('⚠️ Proxy returned non-200 status, but endpoint is reachable');
        return false;
      }
    } catch (error) {
      console.error('❌ Connectivity test failed:', error.message);
      return false;
    }
  }

  /**
   * Test with a simple prompt
   */
  async testSimplePrompt() {
    console.log('🧪 Testing simple prompt...');
    
    const testPrompt = "Hello! Please respond with exactly: 'OpenRouter proxy is working correctly!'";
    
    const requestBody = {
      model: this.model,
      messages: [
        {
          role: 'user',
          content: testPrompt
        }
      ],
      temperature: 0.1, // Low temperature for consistent response
      max_tokens: 50
    };

    try {
      console.log('📤 Sending test request...');
      console.log('📋 Request body:', JSON.stringify(requestBody, null, 2));
      
      const response = await fetch(this.baseUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      });

      console.log(`📡 Response status: ${response.status}`);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error(`❌ API error: ${response.status} - ${errorText}`);
        return false;
      }

      const responseData = await response.json();
      console.log('📥 Full response:', JSON.stringify(responseData, null, 2));
      
      if (responseData.choices && responseData.choices.length > 0) {
        const generatedText = responseData.choices[0].message.content;
        console.log('✅ Generated response:', generatedText);
        console.log('📊 Response length:', generatedText.length, 'characters');
        return true;
      } else {
        console.error('❌ No choices in response');
        return false;
      }

    } catch (error) {
      console.error('❌ Simple prompt test failed:', error.message);
      return false;
    }
  }

  /**
   * Test with Facebook-like data
   */
  async testFacebookData() {
    console.log('📘 Testing with Facebook-like data...');
    
    const mockFacebookData = {
      "user_info": {
        "name": "Test User",
        "age": 25,
        "location": "Test City"
      },
      "posts": [
        {
          "content": "Just had an amazing day at the beach!",
          "timestamp": "2024-01-15",
          "reactions": ["like", "love"]
        },
        {
          "content": "Working on a new project, feeling excited!",
          "timestamp": "2024-01-14",
          "reactions": ["like"]
        }
      ],
      "interests": ["technology", "travel", "photography"]
    };

    const testPrompt = `Analyze this Facebook data and provide a brief personality assessment:

${JSON.stringify(mockFacebookData, null, 2)}

Please provide a 2-3 sentence psychological profile.`;

    const requestBody = {
      model: this.model,
      messages: [
        {
          role: 'user',
          content: testPrompt
        }
      ],
      temperature: this.temperature,
      max_tokens: 200
    };

    try {
      console.log('📤 Sending Facebook data test...');
      
      const response = await fetch(this.baseUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      });

      console.log(`📡 Response status: ${response.status}`);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error(`❌ API error: ${response.status} - ${errorText}`);
        return false;
      }

      const responseData = await response.json();
      
      if (responseData.choices && responseData.choices.length > 0) {
        const generatedText = responseData.choices[0].message.content;
        console.log('✅ Facebook data analysis result:');
        console.log(generatedText);
        console.log('📊 Analysis length:', generatedText.length, 'characters');
        return true;
      } else {
        console.error('❌ No choices in response');
        return false;
      }

    } catch (error) {
      console.error('❌ Facebook data test failed:', error.message);
      return false;
    }
  }

  /**
   * Test error handling
   */
  async testErrorHandling() {
    console.log('⚠️ Testing error handling...');
    
    // Test with invalid model
    const requestBody = {
      model: 'invalid-model-name',
      messages: [
        {
          role: 'user',
          content: 'This should fail'
        }
      ],
      temperature: 0.7,
      max_tokens: 50
    };

    try {
      const response = await fetch(this.baseUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      });

      console.log(`📡 Error test response status: ${response.status}`);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.log('✅ Error handling working correctly - got expected error:', errorText);
        return true;
      } else {
        console.log('⚠️ Expected error but got success - this might indicate an issue');
        return false;
      }

    } catch (error) {
      console.log('✅ Error handling working correctly - caught error:', error.message);
      return true;
    }
  }

  /**
   * Run all tests
   */
  async runAllTests() {
    console.log('🚀 Starting OpenRouter Proxy Tests...');
    console.log('='.repeat(50));
    
    const results = {
      connectivity: false,
      simplePrompt: false,
      facebookData: false,
      errorHandling: false
    };

    // Test 1: Connectivity
    console.log('\n1️⃣ CONNECTIVITY TEST');
    console.log('-'.repeat(30));
    results.connectivity = await this.testConnectivity();
    
    // Test 2: Simple Prompt
    console.log('\n2️⃣ SIMPLE PROMPT TEST');
    console.log('-'.repeat(30));
    results.simplePrompt = await this.testSimplePrompt();
    
    // Test 3: Facebook Data
    console.log('\n3️⃣ FACEBOOK DATA TEST');
    console.log('-'.repeat(30));
    results.facebookData = await this.testFacebookData();
    
    // Test 4: Error Handling
    console.log('\n4️⃣ ERROR HANDLING TEST');
    console.log('-'.repeat(30));
    results.errorHandling = await this.testErrorHandling();
    
    // Summary
    console.log('\n📊 TEST RESULTS SUMMARY');
    console.log('='.repeat(50));
    console.log(`🔗 Connectivity: ${results.connectivity ? '✅ PASS' : '❌ FAIL'}`);
    console.log(`🧪 Simple Prompt: ${results.simplePrompt ? '✅ PASS' : '❌ FAIL'}`);
    console.log(`📘 Facebook Data: ${results.facebookData ? '✅ PASS' : '❌ FAIL'}`);
    console.log(`⚠️ Error Handling: ${results.errorHandling ? '✅ PASS' : '❌ FAIL'}`);
    
    const passedTests = Object.values(results).filter(Boolean).length;
    const totalTests = Object.keys(results).length;
    
    console.log(`\n🎯 Overall: ${passedTests}/${totalTests} tests passed`);
    
    if (passedTests === totalTests) {
      console.log('🎉 All tests passed! OpenRouter proxy is working correctly.');
    } else {
      console.log('⚠️ Some tests failed. Check the logs above for details.');
    }
    
    return results;
  }
}

// Export for use in other files
export default OpenRouterTester;

// If running directly in browser console
if (typeof window !== 'undefined') {
  window.OpenRouterTester = OpenRouterTester;
  window.testOpenRouter = async () => {
    const tester = new OpenRouterTester();
    return await tester.runAllTests();
  };
}
