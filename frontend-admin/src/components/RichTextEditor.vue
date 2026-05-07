<template>
  <div>
    <div style="display:flex; flex-wrap:wrap; gap:8px; margin-bottom:10px;">
      <el-button-group>
        <el-button size="small" @click="cmd('toggleBold')" :type="isActive('bold') ? 'primary' : 'default'">B</el-button>
        <el-button size="small" @click="cmd('toggleItalic')" :type="isActive('italic') ? 'primary' : 'default'">I</el-button>
        <el-button size="small" @click="cmd('toggleStrike')" :type="isActive('strike') ? 'primary' : 'default'">S</el-button>
      </el-button-group>

      <el-button-group>
        <el-button size="small" @click="setHeading(1)" :type="isHeading(1) ? 'primary' : 'default'">H1</el-button>
        <el-button size="small" @click="setHeading(2)" :type="isHeading(2) ? 'primary' : 'default'">H2</el-button>
        <el-button size="small" @click="setHeading(3)" :type="isHeading(3) ? 'primary' : 'default'">H3</el-button>
        <el-button size="small" @click="setParagraph" :type="isActive('paragraph') ? 'primary' : 'default'">P</el-button>
      </el-button-group>

      <el-button-group>
        <el-button size="small" @click="cmd('toggleBulletList')" :type="isActive('bulletList') ? 'primary' : 'default'">• List</el-button>
        <el-button size="small" @click="cmd('toggleOrderedList')" :type="isActive('orderedList') ? 'primary' : 'default'">1. List</el-button>
        <el-button size="small" @click="cmd('toggleBlockquote')" :type="isActive('blockquote') ? 'primary' : 'default'">Quote</el-button>
        <el-button size="small" @click="cmd('toggleCodeBlock')" :type="isActive('codeBlock') ? 'primary' : 'default'">Code</el-button>
      </el-button-group>

      <el-button-group>
        <el-button size="small" @click="setAlign('left')">Left</el-button>
        <el-button size="small" @click="setAlign('center')">Center</el-button>
        <el-button size="small" @click="setAlign('right')">Right</el-button>
      </el-button-group>

      <el-button-group>
        <el-button size="small" @click="setLink">Link</el-button>
        <el-button size="small" @click="unsetLink">Unlink</el-button>
      </el-button-group>

      <el-button-group>
        <el-button size="small" @click="pickImage" :loading="uploading">Image</el-button>
        <el-button size="small" @click="undo" :disabled="!canUndo">Undo</el-button>
        <el-button size="small" @click="redo" :disabled="!canRedo">Redo</el-button>
      </el-button-group>

      <input ref="fileInput" type="file" accept="image/*" style="display:none" @change="onFileChange" />
    </div>

    <div class="editor-card">
      <EditorContent :editor="editor" />
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, ref, watch } from "vue";
import { ElMessage } from "element-plus";

import { Editor, EditorContent } from "@tiptap/vue-3";
import StarterKit from "@tiptap/starter-kit";
import Link from "@tiptap/extension-link";
import Image from "@tiptap/extension-image";
import Placeholder from "@tiptap/extension-placeholder";
import TextAlign from "@tiptap/extension-text-align";

import http from "../api/http";

const props = defineProps({
  modelValue: { type: String, default: "" },
  placeholder: { type: String, default: "Write something..." },
});
const emit = defineEmits(["update:modelValue"]);

const editor = new Editor({
  extensions: [
    StarterKit,
    Link.configure({ openOnClick: false }),
    Image,
    Placeholder.configure({ placeholder: props.placeholder }),
    TextAlign.configure({ types: ["heading", "paragraph"] }),
  ],
  content: props.modelValue || "",
  onUpdate: ({ editor }) => {
    emit("update:modelValue", editor.getHTML());
  },
});

watch(
  () => props.modelValue,
  (v) => {
    if (!editor) return;
    const current = editor.getHTML();
    if ((v || "") !== current) editor.commands.setContent(v || "", false);
  }
);

onBeforeUnmount(() => editor?.destroy());

function cmd(name) {
  editor.chain().focus()[name]().run();
}
function isActive(name) {
  return editor.isActive(name);
}
function isHeading(level) {
  return editor.isActive("heading", { level });
}
function setHeading(level) {
  editor.chain().focus().toggleHeading({ level }).run();
}
function setParagraph() {
  editor.chain().focus().setParagraph().run();
}
function setAlign(alignment) {
  editor.chain().focus().setTextAlign(alignment).run();
}

function setLink() {
  const prev = editor.getAttributes("link").href || "";
  const url = window.prompt("Enter URL", prev);
  if (url === null) return;
  if (url.trim() === "") {
    editor.chain().focus().extendMarkRange("link").unsetLink().run();
    return;
  }
  editor.chain().focus().extendMarkRange("link").setLink({ href: url.trim() }).run();
}
function unsetLink() {
  editor.chain().focus().extendMarkRange("link").unsetLink().run();
}

const canUndo = computed(() => editor?.can().chain().focus().undo().run() ?? false);
const canRedo = computed(() => editor?.can().chain().focus().redo().run() ?? false);
function undo() { editor.chain().focus().undo().run(); }
function redo() { editor.chain().focus().redo().run(); }

const fileInput = ref(null);
const uploading = ref(false);

function pickImage() {
  fileInput.value?.click();
}

async function onFileChange(e) {
  const file = e.target.files?.[0];
  e.target.value = "";
  if (!file) return;

  uploading.value = true;
  try {
    const fd = new FormData();
    fd.append("file", file);

    const res = await http.post("/admin/uploads/", fd);
    const url = res.data?.url;
    if (!url) throw new Error("no url");

    editor.chain().focus().setImage({ src: url }).run();
    ElMessage.success("Image uploaded");
  } catch {
    ElMessage.error("Upload failed: check backend /api/admin/uploads/");
  } finally {
    uploading.value = false;
  }
}
</script>

<style scoped>
.editor-card{
  background: var(--card);
  border-radius: 14px;
  box-shadow: var(--shadow);
  padding: 12px;
}

/* TipTap 编辑区域样式 */
:deep(.ProseMirror){
  min-height: 260px;
  outline: none;
  line-height: 1.8;
  font-size: 14px;
  color: var(--text);
}

:deep(.ProseMirror p){ margin: 0 0 10px; }
:deep(.ProseMirror h1){ font-size: 26px; margin: 14px 0 10px; }
:deep(.ProseMirror h2){ font-size: 22px; margin: 14px 0 10px; }
:deep(.ProseMirror h3){ font-size: 18px; margin: 14px 0 10px; }
:deep(.ProseMirror blockquote){
  border-left: 4px solid rgba(0,0,0,0.15);
  margin: 12px 0;
  padding: 6px 12px;
  color: var(--muted);
}
:deep(.ProseMirror img){
  max-width: 100%;
  border-radius: 10px;
  display: block;
  margin: 10px 0;
}
:deep(.ProseMirror pre){
  background: rgba(0,0,0,0.06);
  padding: 10px;
  border-radius: 10px;
  overflow: auto;
}
html.dark :deep(.ProseMirror pre){
  background: rgba(255,255,255,0.08);
}
</style>
