<template>
<div>
    <div v-if="!creatingAccount" class="container">
      <div class="row justify-content-center">
        <div class="card" style="width: 18rem; margin:2rem">
          <div class="card-body">
            <div class="form-label-group">
              <label for="inputEmail">Username</label>
              <input type="username" id="inputUsername" class="form-control"
              placeholder="Username" required autofocus v-model="username">
            </div>
            <div class="form-label-group">
              <br>
              <label for="inputPassword">Password</label>
              <input type="password" id="inputPassword" class="form-control"
              placeholder="Password" required v-model="password">
            </div>
          </div>
          <button class="btn btn-primary btn-lg" style=" margin:2rem" :disabled="isEmpty()" @click="checkLogin()">LogIn</button>
          <button class="btn btn-success btn-lg" style=" margin:2rem" @click="goCreate">Create Account</button>
          <button class="btn btn-secondary btn-lg" style=" margin:2rem" @click="goMatches()">Back To Matches</button>
        </div>
      </div>
    </div>
    <div v-else class="container">
      <div>
        <b-form @submit="onSubmit" @reset="onReset" v-if="show">
          <b-form-group id="input-group-1" label="Your name:" label-for="input-1">
            <b-form-input
              id="input-1"
              v-model="addUserForm.username"
              placeholder="Enter name"
              required
            ></b-form-input>
          </b-form-group>
          <b-form-group id="input-group-2" label="Your password:" label-for="input-2">
            <b-form-input
              type="password"
              id="input-2"
              v-model="addUserForm.password"
              placeholder=""
              required
            ></b-form-input>
          </b-form-group>
          <b-form-group id="input-group-3" label="Repeat password:" label-for="input-3">
            <b-form-input
              type="password"
              id="input-3"
              v-model="checkPass"
              placeholder=""
              required
            ></b-form-input>
          </b-form-group>
          <b-button type="submit" variant="primary">Submit</b-button>
          <b-button type="reset" variant="danger">Reset</b-button>
        </b-form>
        <button class="btn btn-secondary btn-lg" style=" margin:2rem" @click="creatingAccount = false">Back</button>
      </div>
    </div>
</div>
</template>

<script>
import axios from 'axios'

export default {
  data () {
    return {
      show: true,
      creatingAccount: false,
      addUserForm: {
        username: null,
        password: null
      },
      checkPass: null,
      message: 'Login',
      logged: false,
      username: '',
      password: '',
      token: null
    }
  },
  methods: {
    isEmpty () {
      if (this.username.length === 0 || this.password.length === 0) {
        return true
      } else {
        return false
      }
    },
    goMatches () {
      this.$router.push({ path: '/' })
    },
    goCreate () {
      this.initCreateForm()
      this.password = ''
      this.creatingAccount = true
    },
    checkLogin () {
      const parameters = {
        username: this.username,
        password: this.password
      }
      const path = 'https://a11-sportsmaster.herokuapp.com/'
      axios.post(path, parameters)
        .then((res) => {
          this.logged = true
          this.token = res.data.token
          this.$router.push({ path: '/', query: { username: this.username, logged: this.logged, token: this.token } })
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error)
          this.password = ''
          alert('Username or Password incorrect')
        })
    },
    initCreateForm () {
      this.creatingAccount = true
      this.addUserForm.username = null
      this.addUserForm.password = null
      this.checkPass = null
    },
    onReset () {
      this.initCreateForm()
    },
    onSubmit (e) {
      e.preventDefault()
      if (this.addUserForm.password !== this.checkPass) {
        alert('Passwords are not the same')
      } else {
        const parameters = {
          username: this.addUserForm.username,
          password: this.addUserForm.password
        }
        const path = 'https://a11-sportsmaster.herokuapp.com/account/'
        axios.post(path, parameters)
          .then((res) => {
            this.creatingAccount = false
            this.username = this.addUserForm.username
            this.password = ''
            alert('User created successfully')
          })
          .catch((error) => {
            // eslint-disable-next-line
            alert('Username not available')
            console.error(error)
          })
      }
    }
  }
}
</script>

<style scoped>

</style>
