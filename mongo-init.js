db.getCollection("Category").insertMany([
  {
    "name": "默认分类",
    "description": "系统默认分类",
    "order": 0,
    "icon_url": null
  }
]);

db.getCollection("AIExperience").insertMany([
  {
    "title": "梵高风格转换",
    "description": "让你的照片瞬间拥有星空般的油画质感",
    "experience_type": "image-to-image",
    "default_prompt": "Post-impressionist style, Van Gogh, oil painting, thick brushwork, vibrant cypress trees and swirling stars",
    "cover_url": null,
    "config": {
      "ref_images": [],
      "storage_dir": null
    },
    "tags": ["艺术", "滤镜"],
    "order": 1
  },
  {
    "title": "专业翻译官",
    "description": "精通各种语言的地道翻译助手",
    "experience_type": "chat",
    "default_prompt": "你是一位精通多国语言的翻译大师。请将用户输入的任何内容翻译为地道的英语，并给出重点词汇的解释。",
    "cover_url": null,
    "config": {},
    "tags": ["办公", "效率"],
    "order": 2
  }
]);
