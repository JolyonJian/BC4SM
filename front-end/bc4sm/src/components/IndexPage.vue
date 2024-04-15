<template>
  <div class="common-layout page-style">
    <el-container style="height: 100%;">
      <el-header class="black-white">
        <div class="header-content">Blockchain-based secure messaging</div>
      </el-header>
      <el-main style="background-color: #f5f5f5;">
        <el-row>
          <el-col :span="24">
            <div>
              <el-card style="max-width: 100%; text-align: left;">
                <template #header>
                  <div class="card-header">
                    <span>User List</span>
                  </div>
                </template>
                <el-row class="row-style">
                  <el-col :span="24">
                    <div>
                      <el-button type="primary" @click="refreshUserList">
                        Refresh
                      </el-button>
                    </div>
                  </el-col>
                </el-row>
                <el-row>
                  <el-col :span="24">
                    <div>
                      <el-table border stripe="true" :data="userList" style="width: 100%;">
                        <el-table-column type="selection" width="55"></el-table-column>
                        <el-table-column type="index" label="index" width="100"></el-table-column>
                        <el-table-column prop="name" label="user"></el-table-column>
                        <el-table-column prop="addr" label="blockchain address"></el-table-column>
                      </el-table>
                    </div>
                  </el-col>
                </el-row>
                <div></div>
              </el-card>
            </div>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="24">
            <el-card style="max-width: 100%; text-align: left; margin-top: 2%;">
              <template #header>
                <div class="card-header">
                  <span>Secure Messaging</span>
                </div>
              </template>
              <div class="m-4">
                <p>Sender</p>
                <el-select v-model="senderValue" :disabled="selectDisabled" placeholder="please select sender"
                  style="width: 240px;">
                  <el-option v-for="item in options" :key="item.value" :label="item.label" :value="item.value" />
                </el-select>
              </div>
              <div class="m-4">
                <p>Receiver</p>
                <el-select v-model="receiverValue" :disabled="selectDisabled" placeholder="please select sender"
                  style="width: 240px;">
                  <el-option v-for="item in options" :key="item.value" :label="item.label" :value="item.value" />
                </el-select>
              </div>
              <el-divider />
              <div class="m-4">
                <p>Generate Key</p>
                <el-result v-if="isgenerated" style="
                    width: 10%;
                    padding: 0;
                    --el-result-title-font-size: 12px;
                    --el-result-title-margin-top: 0;
                  " icon="success" :title="keystatus"></el-result>
                <el-button v-if="!isgenerated" v-loading="keystatusisloading" type="primary"
                  :disabled="generatekeydisabled" @click="generateKey">
                  generate
                </el-button>
              </div>
              <el-divider />
              <div class="m-4">
                <p>Sending data via blockchain</p>
                <FileUpload @file-selected="handleFileSelected" @file-uploaded="handleFileUploaded" />
                <div v-if="isuploadprogress" style="display: flex; align-items: center;">
                  <p style="margin-right: 10px; font-size: 12px;">progress</p>
                  <el-progress style="width: 640px;" :percentage="uploadprogress" :indeterminate="uploadprogressflow" />
                </div>
              </div>
              <el-divider />
              <div class="m-4">
                <p>Performance evaluation</p>
                <el-row>
                  <el-col :span="8">
                    <el-statistic title="Key generation latency (ms)" :value="kgltime" />
                  </el-col>
                  <el-col :span="8">
                    <el-statistic title="Data encryption latency (ms)" :value="deltime" />
                  </el-col>
                  <el-col :span="8">
                    <el-statistic title="Data upload latency (ms)" :value="dultime" />
                  </el-col>
                </el-row>
              </div>
            </el-card>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="24">
            <el-card style="max-width: 100%; text-align: left;">
              <div class="m-4">
                <p>Receiver</p>
              </div>
              <el-divider />
              <div class="m-4">
                <p>Progress</p>
                <el-timeline style="max-width: 600px;">
                  <el-timeline-item v-for="(activity, index) in activities" :key="index"
                    :timestamp="activity.timestamp">
                    {{ activity.content }}
                    <el-progress style="width: 640px;" :percentage="activity.perc" status="success"
                      :indeterminate="activity.ind" :duration="5" />
                  </el-timeline-item>
                </el-timeline>
                <el-text class="mx-1" type="success">{{msgdataloc}}</el-text>
              </div>
              <el-divider />
              <div class="m-4">
                <p>Performance evaluation</p>
                <el-row>
                  <el-col :span="8">
                    <el-statistic title="Config acquisition latency (ms)" :value="caltime" />
                  </el-col>
                  <el-col :span="8">
                    <el-statistic title="Data acquisition latency (ms)" :value="daltime" />
                  </el-col>
                  <el-col :span="8">
                    <el-statistic title="Data decryption latency (ms)" :value="ddltime" />
                  </el-col>
                </el-row>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-main>
      <el-footer class="black-white">
        <div class="footer-content">Copyright © 2024</div>
      </el-footer>
    </el-container>
  </div>
</template>

<script lang="ts">
import FileUpload from '@/components/FileUpload.vue'

import { defineComponent, useAttrs, ref, Ref } from 'vue'

import { ElMessage } from 'element-plus'

import { useTransition } from '@vueuse/core'
import axios from 'axios'

export default defineComponent({
  name: 'IndexPage',
  props: {
    msg: String,
  },
  components: {
    FileUpload,
  },
  data() {
    const userList = ref([])

    const senderValue = ref('')
    const receiverValue = ref('')
    interface Option {
      value: string
      label: string
    }
    const options: Ref<Option[]> = ref([])

    const keystatus = ref('')

    const uploadUrl = ref<string>('/file/upload')
    let file = ref<File | null>(null)
    const handleFileSelected = (selectedFile: File) => {
      file.value = selectedFile
    }

    const source1 = ref(0)
    const kgltime = useTransition(source1, { duration: 1000 })
    const source2 = ref(0)
    const deltime = useTransition(source2, { duration: 1000 })
    const source3 = ref(0)
    const dultime = useTransition(source3, { duration: 1000 })

    const percentage = ref()

    const activities = [
      {
        content: 'Get session configuration',
        timestamp: '',
        perc: 0,
        ind: false,
      },
      {
        content: 'Get cipher text',
        timestamp: '',
        perc: 0,
        ind: false,
      },
      {
        content: 'Data decryption',
        timestamp: '',
        perc: 0,
        ind: false,
      },
    ]

    const source4 = ref(0)
    const caltime = useTransition(source4, { duration: 1000 })
    const source5 = ref(0)
    const daltime = useTransition(source5, { duration: 1000 })
    const source6 = ref(0)
    const ddltime = useTransition(source6, { duration: 1000 })

    return {
      userList: [],

      senderValue,
      receiverValue,
      options,
      selectDisabled: false,

      generatekeydisabled: false,
      isgenerated: false,
      keystatus,
      keystatusisloading: false,

      uploadUrl,
      handleFileSelected,

      isuploadprogress: false,
      uploadprogress: 0,
      uploadprogressflow: false,

      source1,
      kgltime,
      source2,
      deltime,
      source3,
      dultime,

      source4,
      caltime,
      source5,
      daltime,
      source6,
      ddltime,

      percentage,
      activities,

      msgdataloc: '',
    }
  },
  mounted() {
    this.fetchUserList()
  },
  methods: {
    async fetchUserList() {
      try {
        const response = await axios.get('http://localhost:3000/user/listall')
        let resdata = response.data.user_list
        console.log('数据获取成功', resdata)
        let option_list: { value: any; label: any }[] = []
        for (var i = 0; i < resdata.length; i++) {
          option_list.push({
            value: resdata[i].addr,
            label: resdata[i].name,
          })
        }
        this.userList = resdata
        this.options = option_list
      } catch (error) {
        console.log('数据获取失败', error)
      }
    },
    async refreshUserList() {
      this.userList = []
      await this.fetchUserList()
    },
    async generateKey() {
      if (this.senderValue == '' || this.receiverValue == '') {
        ElMessage({ message: 'Please select sender and receiver!', type: 'error', duration: 2000 }); 'Please select sender and receiver!'
        return;
      }
      try {
        this.keystatusisloading = true
        const response = await axios.post(
          'http://localhost:3000/key/register',
          {
            sender: this.senderValue,
            receiver: this.receiverValue,
          },
        )
        if (response.data.result == 200) {
          this.keystatus = 'Key generation succeed!'
          this.selectDisabled = true
          this.isgenerated = true
          this.keystatusisloading = false
          this.source1 = parseInt(response.data.time)
        } else {
          ElMessage({ message: 'Key generation failed!', type: 'error', duration: 2000 });
          this.keystatusisloading = false
        }
      } catch (error) {
        console.log('error: ', error)
      }
    },
    async handleFileUploaded(uploadedFile: any) {
      this.isuploadprogress = true;
      try {
        const response = await axios.post('http://localhost:3000/send/getkey', {
          sender: this.senderValue,
          receiver: this.receiverValue,
        })
        if (response.data.result == 200) {
          this.uploadprogress = 10
          this.uploadprogressflow = true
          console.log('公钥获取成功！')
          const response = await axios.post('http://localhost:3000/send/encrypt', {
            file: uploadedFile.name
          })
          this.source2 = parseInt(response.data.time)
          if (response.data.result == 200) {
            this.uploadprogress = 15
            this.uploadprogressflow = true
            console.log('数据加密成功！')
            const response = await axios.post('http://localhost:3000/send/blockchain', {
              sender: this.senderValue,
              receiver: this.receiverValue,
            });
            this.source3 = parseInt(response.data.time)
            if (response.data.result == 200) {
              this.uploadprogress = 100
              this.uploadprogressflow = false
              console.log('数据上链成功！')
              this.activities[0] = {
                content: 'Get session configuration',
                timestamp: new Date().toLocaleString(),
                perc: 100,
                ind: true,
              }
              const response = await axios.post('http://localhost:3000/receive/conf', {
                receiver: this.receiverValue,
              });
              this.source4 = parseInt(response.data.time)
              if (response.data.result == 200) {
                console.log('解密配置获取成功！')
                this.activities[0] = {
                  content: 'Get session configuration',
                  timestamp: new Date().toLocaleString(),
                  perc: 100,
                  ind: false,
                }
                this.activities[1] = {
                  content: 'Get cipher text',
                  timestamp: new Date().toLocaleString(),
                  perc: 100,
                  ind: true,
                }
                const response = await axios.post('http://localhost:3000/receive/data', {
                  receiver: this.receiverValue,
                })
                this.source5 = parseInt(response.data.time)
                if (response.data.result == 200) {
                  console.log('密文数据获取成功！')
                  this.activities[1] = {
                    content: 'Get cipher text',
                    timestamp: new Date().toLocaleString(),
                    perc: 100,
                    ind: false,
                  }
                  this.activities[2] = {
                    content: 'Data decryption',
                    timestamp: new Date().toLocaleString(),
                    perc: 100,
                    ind: true,
                  }
                  const response = await axios.post('http://localhost:3000/receive/decrypt',{
                    receiver: this.receiverValue,
                    file: uploadedFile.name
                  })
                  this.source6 = parseInt(response.data.time)
                  if (response.data.result == 200) {
                    console.log('数据解密成功！')
                    this.activities[2] = {
                      content: 'Data decryption',
                      timestamp: new Date().toLocaleString(),
                      perc: 100,
                      ind: false,
                    }
                    this.msgdataloc = 'The message has been saved in the /results directory.'
                  } else {
                    console.log('数据解密失败！')
                  }
                } else {
                  console.log('密文数据获取失败！')
                }
              } else {
                console.log('解密配置获取失败！')
              }
            } else {
              console.log('数据上链失败！')
            }
          } else {
            console.log('数据加密失败！')
          }
        } else {
          console.log('数据加密失败！')
        }
      }
      catch (error) {
        console.log('公钥获取失败！', error)
      }
    }
  }
}
)
</script>

<style>
.demo-progress .el-progress--line {
  margin-bottom: 15px;
  max-width: 600px;
}

.page-style {
  font-family: 'PingFang SC', sans-serif;
  margin-left: 1%;
  margin-right: 1%;
  height: 100%;
}

.center-content {
  display: flex;
  justify-content: center;
  /* 水平居中 */
  align-items: center;
  /* 垂直居中 */
  height: 100%;
}

.header-content {
  display: flex;
  justify-content: center;
  /* 水平居中 */
  align-items: center;
  /* 垂直居中 */
  height: 100%;
}

.footer-content {
  display: flex;
  justify-content: center;
  /* 水平居中 */
  align-items: center;
  /* 垂直居中 */
  height: 100%;
  font-size: 12px;
}

.row-style {
  margin-top: 1%;
  margin-bottom: 1%;
}

.black-white {
  background-color: black;
  color: white;
}
</style>
