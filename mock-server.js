// 简化的 Mock 后端服务器
// 用于前端开发和演示

const http = require('http');
const url = require('url');

const PORT = 8000;

// 模拟数据存储
const tasks = new Map();
let taskIdCounter = 1;

// 生成任务ID
function generateTaskId(type) {
  const prefix = type === 'image' ? 'img' : 'vid';
  return `${prefix}_${Date.now().toString(36)}${Math.random().toString(36).substr(2, 5)}`;
}

// CORS 头
function setCORSHeaders(res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
}

// 发送 JSON 响应
function sendJSON(res, data, statusCode = 200) {
  res.writeHead(statusCode, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify(data));
}

// 路由处理
const routes = {
  // 健康检查
  'GET /api/health': (req, res) => {
    sendJSON(res, { code: 200, data: { status: 'ok' } });
  },

  // 登录
  'POST /api/auth/login': (req, res) => {
    sendJSON(res, {
      code: 200,
      data: {
        token: 'mock_token_' + Date.now(),
        token_type: 'bearer',
        user: {
          id: 1,
          email: 'user@example.com',
          name: '演示用户',
          avatar: ''
        }
      }
    });
  },

  // 注册
  'POST /api/auth/register': (req, res) => {
    sendJSON(res, { code: 200, message: '注册成功' });
  },

  // 获取当前用户
  'GET /api/auth/me': (req, res) => {
    sendJSON(res, {
      code: 200,
      data: {
        id: 1,
        email: 'user@example.com',
        name: '演示用户',
        avatar: ''
      }
    });
  },

  // 获取图片模型列表
  'GET /api/images/models': (req, res) => {
    sendJSON(res, {
      code: 200,
      data: [
        {
          id: 'doubao-seedream-4-0-250828',
          name: 'Seedream 4.0',
          description: '豆包图片生成模型',
          supported_ratios: ['1:1', '9:16', '16:9', '3:4', '4:3'],
          supported_resolutions: ['512', '768', '1024', '2048'],
        },
        {
          id: 'doubao-seedream-4-5-251128',
          name: 'Seedream 4.5',
          description: '豆包图片生成模型增强版',
          supported_ratios: ['1:1', '9:16', '16:9', '3:4', '4:3'],
          supported_resolutions: ['512', '768', '1024', '2048'],
        },
        {
          id: 'doubao-seedream-5-0-260128',
          name: 'Seedream 5.0',
          description: '豆包图片生成模型最新版',
          supported_ratios: ['1:1', '9:16', '16:9', '3:4', '4:3'],
          supported_resolutions: ['512', '768', '1024', '2048'],
        },
      ]
    });
  },

  // 创建图片生成任务
  'POST /api/images/generations': (req, res) => {
    const taskId = generateTaskId('image');
    const task = {
      id: taskId,
      type: 'image',
      status: 'pending',
      createdAt: new Date().toISOString(),
    };
    tasks.set(taskId, task);

    // 模拟异步处理
    setTimeout(() => {
      task.status = 'processing';
      setTimeout(() => {
        task.status = 'completed';
        task.output_urls = ['https://via.placeholder.com/1024x1024/1890ff/ffffff?text=Generated+Image'];
        task.completedAt = new Date().toISOString();
      }, 5000);
    }, 1000);

    sendJSON(res, {
      code: 200,
      data: {
        task_id: taskId,
        status: 'pending',
        message: '图片生成任务已创建'
      }
    });
  },

  // 查询图片任务
  'GET /api/images/generations/': (req, res, path) => {
    const taskId = path.split('/').pop();
    const task = tasks.get(taskId);
    if (task) {
      sendJSON(res, {
        code: 200,
        data: {
          task_id: taskId,
          status: task.status,
          progress: task.status === 'completed' ? 100 : task.status === 'processing' ? 50 : 0,
          output_urls: task.output_urls || [],
          created_at: task.createdAt,
          completed_at: task.completedAt,
        }
      });
    } else {
      sendJSON(res, { code: 404, message: '任务不存在' }, 404);
    }
  },

  // 获取图片任务列表
  'GET /api/images/generations': (req, res) => {
    const taskList = Array.from(tasks.values())
      .filter(t => t.type === 'image')
      .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));

    sendJSON(res, {
      code: 200,
      data: {
        items: taskList,
        total: taskList.length,
        page: 1,
        page_size: 10,
      }
    });
  },

  // 获取视频模型列表
  'GET /api/videos/models': (req, res) => {
    sendJSON(res, {
      code: 200,
      data: [
        {
          id: 'doubao-seedance-2-0-260128',
          name: 'Seedance 2.0',
          description: '豆包视频生成模型',
          supported_ratios: ['9:16', '16:9', '1:1'],
          supported_resolutions: ['480p', '720p', '1080p'],
          max_duration: 10,
        },
        {
          id: 'doubao-seedance-2-0-fast-260128',
          name: 'Seedance 2.0 Fast',
          description: '豆包视频生成模型快速版',
          supported_ratios: ['9:16', '16:9', '1:1'],
          supported_resolutions: ['480p', '720p', '1080p'],
          max_duration: 10,
        },
      ]
    });
  },

  // 创建视频生成任务
  'POST /api/videos/generations': (req, res) => {
    const taskId = generateTaskId('video');
    const { prompt, model, ratio, duration, with_audio, image_url, video_url, audio_url } = req.body;
    
    const task = {
      id: taskId,
      type: 'video',
      status: 'pending',
      model: model || 'doubao-seedance-2-0-260128',
      prompt: prompt || '',
      ratio: ratio || '9:16',
      duration: duration || 5,
      withAudio: with_audio || false,
      hasImage: !!image_url,
      hasVideo: !!video_url,
      hasAudio: !!audio_url,
      createdAt: new Date().toISOString(),
    };
    tasks.set(taskId, task);

    // 模拟异步处理（视频生成时间更长）
    setTimeout(() => {
      task.status = 'processing';
      setTimeout(() => {
        task.status = 'completed';
        task.output_urls = ['https://via.placeholder.com/720x1280/52c41a/ffffff?text=Generated+Video'];
        task.completedAt = new Date().toISOString();
      }, 10000);
    }, 1000);

    sendJSON(res, {
      code: 200,
      data: {
        task_id: taskId,
        status: 'pending',
        message: '视频生成任务已创建'
      }
    });
  },

  // 查询视频任务
  'GET /api/videos/generations/': (req, res, path) => {
    const taskId = path.split('/').pop();
    const task = tasks.get(taskId);
    if (task) {
      sendJSON(res, {
        code: 200,
        data: {
          task_id: taskId,
          status: task.status,
          progress: task.status === 'completed' ? 100 : task.status === 'processing' ? 50 : 0,
          output_urls: task.output_urls || [],
          created_at: task.createdAt,
          completed_at: task.completedAt,
        }
      });
    } else {
      sendJSON(res, { code: 404, message: '任务不存在' }, 404);
    }
  },

  // 获取视频任务列表
  'GET /api/videos/generations': (req, res) => {
    const taskList = Array.from(tasks.values())
      .filter(t => t.type === 'video')
      .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));

    sendJSON(res, {
      code: 200,
      data: {
        items: taskList,
        total: taskList.length,
        page: 1,
        page_size: 10,
      }
    });
  },

  // 任务统计
  'GET /api/tasks/stats': (req, res) => {
    const allTasks = Array.from(tasks.values());
    sendJSON(res, {
      code: 200,
      data: {
        today_images: allTasks.filter(t => t.type === 'image').length,
        today_videos: allTasks.filter(t => t.type === 'video').length,
        total_generations: allTasks.length,
        pending_tasks: allTasks.filter(t => t.status === 'pending').length,
        processing_tasks: allTasks.filter(t => t.status === 'processing').length,
      }
    });
  },
};

// 创建服务器
const server = http.createServer((req, res) => {
  setCORSHeaders(res);

  // 处理 OPTIONS 请求
  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  const parsedUrl = url.parse(req.url, true);
  const path = parsedUrl.pathname;

  // 构建路由键
  let routeKey = `${req.method} ${path}`;

  // 处理动态路由（带 ID 的路径）
  if (path.match(/\/api\/(images|videos)\/generations\/[^\/]+$/)) {
    routeKey = `${req.method} /api/$1/generations/`;
  }

  console.log(`${req.method} ${path}`);

  // 查找路由处理器
  const handler = routes[routeKey];

  if (handler) {
    if (req.method === 'POST' || req.method === 'PUT') {
      let body = '';
      req.on('data', chunk => body += chunk);
      req.on('end', () => {
        try {
          req.body = body ? JSON.parse(body) : {};
        } catch (e) {
          req.body = {};
        }
        handler(req, res, path);
      });
    } else {
      handler(req, res, path);
    }
  } else {
    sendJSON(res, { code: 404, message: 'Not Found' }, 404);
  }
});

server.listen(PORT, () => {
  console.log(`🚀 Mock Server running at http://localhost:${PORT}`);
  console.log('');
  console.log('可用的 API 端点:');
  console.log('  POST /api/auth/login');
  console.log('  POST /api/auth/register');
  console.log('  GET  /api/auth/me');
  console.log('  GET  /api/images/models');
  console.log('  POST /api/images/generations');
  console.log('  GET  /api/images/generations/:id');
  console.log('  GET  /api/videos/models');
  console.log('  POST /api/videos/generations');
  console.log('  GET  /api/videos/generations/:id');
  console.log('  GET  /api/tasks/stats');
  console.log('');
  console.log('按 Ctrl+C 停止服务器');
});
