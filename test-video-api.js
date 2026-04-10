/**
 * 测试火山引擎视频生成 API - 使用新的 content 格式
 */
const https = require('https');

const API_KEY = '071dadca-2719-4d75-9f8f-62f2f2587688';
const BASE_URL = 'ark.cn-beijing.volces.com';

// 测试视频生成 API - 使用新的 content 格式
function testVideoAPI() {
  return new Promise((resolve, reject) => {
    const requestBody = {
      "model": "doubao-seedance-2-0-260128",
      "content": [
        {
          "type": "text",
          "text": "一只可爱的猫咪在草地上玩耍，阳光明媚，高清画质"
        }
      ],
      "generate_audio": true,
      "ratio": "16:9",
      "duration": 5,
      "watermark": false
    };

    const data = JSON.stringify(requestBody);

    const options = {
      hostname: BASE_URL,
      port: 443,
      path: '/api/v3/contents/generations/tasks',
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${API_KEY}`,
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(data)
      }
    };

    console.log('=== 测试视频生成 API（新格式）===');
    console.log('URL:', `https://${BASE_URL}/api/v3/contents/generations/tasks`);
    console.log('Model: doubao-seedance-2-0-260128');
    console.log('Request:', JSON.stringify(requestBody, null, 2));
    console.log('');

    const req = https.request(options, (res) => {
      let responseData = '';
      console.log(`Status Code: ${res.statusCode}`);

      res.on('data', (chunk) => {
        responseData += chunk;
      });

      res.on('end', () => {
        console.log('Response:', responseData);
        try {
          const parsed = JSON.parse(responseData);
          resolve({ success: res.statusCode === 200, status: res.statusCode, data: parsed });
        } catch (e) {
          resolve({ success: false, status: res.statusCode, error: responseData });
        }
      });
    });

    req.on('error', (error) => {
      console.error('Request Error:', error);
      reject(error);
    });

    req.write(data);
    req.end();
  });
}

// 运行测试
async function runTests() {
  console.log('=== 火山引擎视频生成 API 测试（新格式）===\n');
  console.log('API Key:', API_KEY.substring(0, 8) + '...');
  console.log('');
  
  try {
    // 测试视频 API
    const videoResult = await testVideoAPI();
    console.log('\n视频生成 API:', videoResult.success ? '✅ 成功' : '❌ 失败');
    
    if (videoResult.success) {
      console.log('\n✅ 视频任务创建成功！');
      console.log('Task ID:', videoResult.data.id);
      console.log('Status:', videoResult.data.status);
    } else {
      console.log('\n错误信息:', videoResult.data?.error?.message || videoResult.data || videoResult.error);
    }
    
  } catch (error) {
    console.error('测试失败:', error);
  }
}

runTests();
