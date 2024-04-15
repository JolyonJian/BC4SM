<template>
  <el-upload ref="upload" class="upload-demo" style="width:240px" :action="uploadAction" :limit="1" :on-exceed="handleExceed"
    :auto-upload="false" @change="handleFileSelected">
    <template #trigger>
      <el-button type="primary">select File</el-button>
    </template>
    <el-button style="margin-left: 3%" class="ml-3" type="success" @click="submitUpload">
      send data
    </el-button>
    <template #tip>
      <div class="el-upload__tip text-red">
        Limit 1 file, new file will cover the old file
      </div>
    </template>
  </el-upload>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { genFileId } from 'element-plus'
import type { UploadInstance, UploadProps, UploadRawFile } from 'element-plus'
import axios from 'axios'

const upload = ref<UploadInstance>()

const uploadedFile = ref<File | null>(null)

const uploadAction =
  'http://localhost:3000/file/upload'

const handleExceed: UploadProps['onExceed'] = (files) => {
  upload.value!.clearFiles()
  const file = files[0] as UploadRawFile
  file.uid = genFileId()
  upload.value!.handleStart(file)
}

const handleFileSelected = (selectedFile: File) => {
  uploadedFile.value = selectedFile
}

const submitUpload = () => {
  upload.value!.submit()
  if (uploadedFile.value) {
    upload.value!.$emit('file-uploaded', uploadedFile.value)
  } else {
    console.error('No file selected.')
  }
}
</script>
