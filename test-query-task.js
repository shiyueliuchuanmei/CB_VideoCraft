/**
 * 查询视频生成任务状态
 */
const https = require('https');

const API_KEY = '071dadca-2719-4d75-9f8f-62f2f2587688';
const BASE_URL = 'ark.cn-beijing.volces.com';
const TASK_ID = 'cgt-20260409135638-f6m84';

function queryTask() {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: BASE_URL,
      port: 443,
      path: `/api/v3/contents/generations/tasks/${TASK_ID}`,
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${API_KEY}`,
      }
    };

    console.log('=== 查询任务状态 ===');
    console.log('Task ID:', TASK_ID);
    console.log('');

    const req = https.request(options, (res) => {
      let responseData = '';
      console.log(`Status Code: ${res.status_code}`);

      res.on('data', (chunk) => {
        responseData += chunk;
      });

      res.on('end', () => {
        console.log('Response:', responseData);
        try {
          const parsed = JSON.parse(responseData);
          resolve({ success: res.statusCode === 200, data: parsed });
        } catch (e) {
          resolve({ success: false, error: responseData });
        }
      });
    });

    req.on('error', (error) => {
      console.error('Request Error:', error);
      reject(error);
    });

    req.end();
  });
}

// 运行查询
async function runQuery() {
  try {
    const result = await queryTask();
    if (result.success) {
      console.log('\n✅ 查询成功');
      console.log('Status:', result.data.status);
      if (result.data.status === 'Succeeded') {
        console.log('Video URL:', result.data.content?.find(c => c.type === 'video_url')?.video_url?.url);
      }
    } else {
      console.log('\n❌ 查询失败');
    }
  } catch (error) {
    console.error('查询失败:', error);
  }
}

runQuery();
