#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""通用 XMind 测试用例生成器

用法：python xmind_generator.py <tree.json> [输出文件名.xmind]

tree.json 格式示例：
{
  "text": "谋诸葛亮",
  "children": [
    {
      "text": "孤熠",
      "children": [
        { "text": "技能完整描述", "children": [...] }
      ]
    }
  ]
}

如果不指定输出文件名，默认取根节点 text + "技能测试用例.xmind"
"""

import json
import os
import sys
import time
import zipfile
import xml.etree.ElementTree as ET


def build_topic(node, next_id, timestamp):
    """递归构建 topic XML 元素"""
    topic = ET.Element("topic")
    topic.set("id", next_id())
    topic.set("timestamp", timestamp)

    title = ET.SubElement(topic, "title")
    title.text = node["text"]

    children = node.get("children", [])
    if children:
        children_elem = ET.SubElement(topic, "children")
        topics_elem = ET.SubElement(children_elem, "topics")
        topics_elem.set("type", "attached")
        for child in children:
            topics_elem.append(build_topic(child, next_id, timestamp))

    return topic


def build_content_xml(tree, next_id, timestamp):
    """构建 content.xml"""
    root_topic = build_topic(tree, next_id, timestamp)

    sheet = ET.Element("sheet")
    sheet.set("id", "1")
    sheet.set("timestamp", timestamp)
    sheet.append(root_topic)

    sheet_title = ET.SubElement(sheet, "title")
    sheet_title.text = tree["text"]

    xmap = ET.Element("xmap-content")
    xmap.set("version", "2.0")
    xmap.set("xmlns", "urn:xmind:xmap:xmlns:content:2.0")
    xmap.set("xmlns:fo", "http://www.w3.org/1999/XSL/Format")
    xmap.set("xmlns:svg", "http://www.w3.org/2000/svg")
    xmap.set("xmlns:xhtml", "http://www.w3.org/1999/xhtml")
    xmap.set("xmlns:xlink", "http://www.w3.org/1999/xlink")
    xmap.append(sheet)

    return '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n' + ET.tostring(xmap, encoding="unicode")


def build_meta_xml():
    """构建 meta.xml"""
    iso_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
        '<meta version="2.0" xmlns="urn:xmind:xmap:xmlns:meta:2.0">\n'
        '    <Author><Name></Name></Author>\n'
        f'    <CreateTime>{iso_time}</CreateTime>\n'
        '    <Creator><Name>XMind</Name></Creator>\n'
        f'    <ModifiedTime>{iso_time}</ModifiedTime>\n'
        '    <Modifier/>\n'
        '</meta>'
    )


def build_styles_xml():
    """构建 styles.xml"""
    return '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n<xmap-styles version="2.0" xmlns="urn:xmind:xmap:xmlns:style:2.0"/>'


def build_manifest_xml():
    """构建 manifest.xml"""
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
        '<manifest xmlns="urn:xmind:xmap:xmlns:manifest:1.0">\n'
        '    <file-entry full-path="content.xml" media-type="text/xml"/>\n'
        '    <file-entry full-path="meta.xml" media-type="text/xml"/>\n'
        '    <file-entry full-path="styles.xml" media-type="text/xml"/>\n'
        '</manifest>'
    )


def generate_xmind(tree, output_path):
    """将用例树数据生成 .xmind 文件"""
    _id_counter = [0]
    timestamp = str(int(time.time()))

    def next_id():
        _id_counter[0] += 1
        return str(_id_counter[0])

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('content.xml', build_content_xml(tree, next_id, timestamp).encode('utf-8'))
        zf.writestr('meta.xml', build_meta_xml().encode('utf-8'))
        zf.writestr('styles.xml', build_styles_xml().encode('utf-8'))
        zf.writestr('META-INF/manifest.xml', build_manifest_xml().encode('utf-8'))

    file_size = os.path.getsize(output_path)
    print(f"XMind 文件已生成：{output_path}")
    print(f"文件大小：{file_size} 字节 ({file_size/1024:.1f} KB)")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    arg = sys.argv[1]

    # 支持 JSON 文件路径 或 直接传入 JSON 字符串
    if os.path.isfile(arg):
        with open(arg, 'r', encoding='utf-8') as f:
            tree = json.load(f)
    else:
        tree = json.loads(arg)

    # 输出文件名：命令行指定 或 取根节点名称
    if len(sys.argv) >= 3:
        output_path = sys.argv[2]
    else:
        root_name = tree.get("text", "未命名")
        output_path = f"{root_name}技能测试用例.xmind"

    generate_xmind(tree, output_path)


if __name__ == "__main__":
    main()
