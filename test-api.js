/**
 * 测试火山引擎 API 可行性 - 使用正确的模型 ID
 */
const https = require('https');

const API_KEY = '071dadca-2719-4d75-9f8f-62f2f2587688';
const BASE_URL = 'ark.cn-beijing.volces.com';

// 测试图片生成 API - 使用正确的模型 ID
function testImageAPI() {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({
      model: 'doubao-seedream-4-0-250828',  // 正确的模型 ID
      prompt: '一只可爱的猫咪，高清，细节丰富',
    });

    const options = {
      hostname: BASE_URL,
      port: 443,
      path: '/api/v3/images/generations',
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${API_KEY}`,
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(data)
      }
    };

    console.log('=== 测试图片生成 API ===');
    console.log('Model: doubao-seedream-4-0-250828');
    console.log('Request:', data);

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

// 测试视频生成 API - 使用正确的模型 ID
function testVideoAPI() {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({
      model: 'doubao-seedance-2-0-260128',  // 正确的模型 ID
      prompt: '一只可爱的猫咪在草地上玩耍',
    });

    const options = {
      hostname: BASE_URL,
      port: 443,
      path: '/api/v3/videos/generations',
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${API_KEY}`,
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(data)
      }
    };

    console.log('\n=== 测试视频生成 API ===');
    console.log('Model: doubao-seedance-2-0-260128');
    console.log('Request:', data);

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
  console.log('=== 火山引擎 API 可行性测试（修正版）===\n');
  console.log('API Key:', API_KEY.substring(0, 8) + '...');
  console.log('');
  
  try {
    // 测试图片 API
    const imageResult = await testImageAPI();
    console.log('\n图片生成 API:', imageResult.success ? '✅ 成功' : '❌ 失败');
    if (!imageResult.success && imageResult.data) {
      console.log('错误:', imageResult.data.error?.message || imageResult.data);
    }
    
    // 测试视频 API
    const videoResult = await testVideoAPI();
    console.log('\n视频生成 API:', videoResult.success ? '✅ 成功' : '❌ 失败');
    if (!videoResult.success && videoResult.data) {
      console.log('错误:', videoResult.data.error?.message || videoResult.data);
    }
    
    console.log('\n=== 测试总结 ===');
    console.log('图片生成:', imageResult.status === 200 ? '✅' : '❌', `(${imageResult.status})`);
    console.log('视频生成:', videoResult.status === 200 ? '✅' : '❌', `(${videoResult.status})`);
    
    if (imageResult.success) {
      console.log('\n✅ 图片生成 API 可用！');
    }
    if (videoResult.success) {
      console.log('✅ 视频生成 API 可用！');
    }
    
  } catch (error) {
    console.error('测试失败:', error);
  }
}

runTests();
