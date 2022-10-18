<template>
  <div id="app">
    <nav class="navbar navbar-expand-sm bg-light">
            <ul class="navbar-nav ml-auto">
                 <li v-if="logged && is_admin && !is_showing_cart" class="nav-item" style="padding-left:15px; padding-right:15px;">
                  <a class="btn btn-outline-primary" @click="editMatch(null)">New Match!</a>
                </li>
                <li v-if="logged && is_admin" class="nav-item" style="padding-left:15px; padding-right:15px;">
                  <a class="btn btn btn-outline-danger disabled" disabled>ADMIN</a>
                </li>
                <li v-if="logged" class="nav-item" style="padding-left:15px; padding-right:15px;">
                  <a class="btn btn-outline-dark disabled">{{username}}</a>
                </li>
                <li v-if="logged && !is_admin" class="nav-item" style="padding-left:15px; padding-right:15px;">
                  <a class="btn btn-outline-warning disabled" disabled>{{display_price(money*100)}}$</a>
                </li>
                <li v-if="logged && !is_match_edit" class="nav-item" style="padding-left:15px; padding-right:15px;">
                  <a class="btn btn-outline-primary" @click="toggleCart">{{ toggleTextCart() }}</a>
                </li>
                <li class="nav-item" style="padding-left:15px; padding-right:15px;">
                  <a class="btn btn-outline-secondary" @click="loginout()">{{logcheck()}}</a>
                </li>
            </ul>
        </nav>
    <h1 v-if="false"> {{ message }} </h1>
    <h4 v-if="false"> Tickets: {{ tickets }} </h4>
    <div v-if="!is_showing_cart && !is_match_edit" class="container">
      <div class="row justify-content-center">
        <div class="card" style="width: 18rem; margin:2rem" v-for="(match) in matches" :key="match.id">
          <img class="card-img-top" v-bind:src="require('../assets/' + match.competition.sport + '.jpg')" alt="Card image cap"/>
          <div class="card-body">
              <h5 class="card-title">{{ match.competition.sport }} - {{ match.competition.category }}</h5>
              <h6>{{ match.competition.name }}</h6>
              <h6><strong>{{ match.local.name }}</strong> ({{ match.local.country }}) vs <strong>{{ match.visitor.name }}</strong> ({{ match.visitor.country }})</h6>
              <h6>{{ match.date.substring(0,10) }}</h6>
              <h6>{{ match.price }} $</h6>
              <h6> Available tickets {{getTickets(match)}} </h6>
              <h6> {{ match.competition.sport }} </h6>
              <button :disabled="!canAddToCart(match)" v-if="logged"  class="btn btn-success btn-lg"  @click="addEventToCart(match)">{{matchButtonText(match)}}</button>
              <button  v-if="logged && is_admin"  class="btn btn-outline-primary"  style="margin: 2px" @click="editMatch(match)">Edit</button>
          </div>
        </div>
      </div>
    </div>
    <div v-else-if="!is_match_edit" class="container" style="padding: 2rem">
      <div v-if="matches_added.length > 0">
        <div class="table-responsive">
          <table class="mx-auto w-auto table" style="white-space: nowrap">
          <thead>
            <tr>
              <th>Sport</th>
              <th>Competition</th>
              <th>Match</th>
              <th>Quantity</th>
              <th>Price(&euro;)</th>
              <th>Total</th>
              <th></th>
            </tr>
          </thead>
          <tbody is="transition-group" name="fade">
            <tr v-for="(match) in matches_added" :key="match.id">
              <td>{{ match.competition.sport }}</td>
              <td>{{ match.competition.name }}</td>
              <td>{{ match.local.name }} vs {{ match.visitor.name }}</td>
              <td>
                {{ match.quantity }}
                <button :disabled="match.quantity >= match.total_available_tickets && !is_admin" @click="increaseQuantity(match)" class="btn btn-success btn-sm">+</button>
                <button :disabled="match.quantity <= 1"  @click="decreaseQuantity(match)" class="btn btn-danger btn-sm">-</button>
                <span v-if="!is_admin">(max {{ match.total_available_tickets  }})</span>
              </td>
              <td>{{ match.price }}</td>
              <td>{{ display_price(100*match_total_price(match)) }}</td>
              <td>
                <button class="btn btn-danger btn-sm" @click="removeFromCart(match)">Eliminar de la cistella</button>
              </td>
            </tr>
          </tbody>
          <tbody>
            <tr>
              <td><span v-if="!canBuy()">Falten {{display_price(100*(cart_total_price()-this.money))}}$</span></td>
              <td></td><td></td><td></td><td></td>
              <td>
                {{ display_price(100*cart_total_price()) }}
              </td>
              <td>
                <button class="btn btn-success btn-sm" :disabled="!canBuy()" @click="finishPurchase()">Finalitzar compra</button>
              </td>
            </tr>
          </tbody>
        </table>
        </div>
      </div>
      <p v-else>La teva cistella està buida.</p>
    </div>
    <div v-else class="container" style="padding:10px;color:black; padding-top: 1em;">
      <div class="row">
        <div class="col-2">
          <h5 style="font-weight: bold;">Teams Local</h5>
          <ul class="list-group" style="cursor:pointer;">
              <li class="list-group-item" v-for="(team) in teams" :key="team.id" v-bind:id="'L'+team.id" @click="pickLocal(team)">
                <span><b>Id:</b> {{team.id}}  <b>Name:</b> {{team.name}}</span>
              </li>
          </ul>
        </div>
        <div class="col-2">
          <h5 style="font-weight: bold;">Teams Visitor</h5>
          <ul class="list-group" style="cursor:pointer;">
              <li class="list-group-item" v-for="(team) in teams" :key="team.id" v-bind:id="'V'+team.id" @click="pickVisitor(team)">
                <span><b>Id:</b> {{team.id}}  <b>Name:</b> {{team.name}}</span>
              </li>
          </ul>
        </div>
        <div class="col-2">
          <h5 style="font-weight: bold;">Competitions</h5>
          <ul class="list-group" style="cursor:pointer;">
            <li class="list-group-item" v-for="(competition) in competitions" :key="competition.id" v-bind:id="competition.id" @click="pickCompetition(competition)">
                <span><b>Id:</b> {{competition.id}}  <b>Name:</b> {{competition.name}}</span>
              </li>
          </ul>
        </div>
        <div class="col-6">
          <h5 style="font-weight: bold;">Partit</h5>
          <div class="row justify-content-center">
            <b-form @submit="onSubmit" @reset="onReset" @delete = "onDelete">
                      <div>
                        <label for="example-datepicker">Choose a date</label>
                        <b-form-datepicker id="example-datepicker" v-model="match_form.date" class="mb-2"></b-form-datepicker>
                      </div>
                      <b-form-group id="input-group-2" label="Price:" label-for="input-2">
                        <b-form-input
                          id="input-2"
                          v-model="match_form.price"
                          :placeholder="match_place_holder.price"
                        ></b-form-input>
                      </b-form-group>
                      <b-form-group id="input-group-3" label="Available tickets:" label-for="input-3">
                        <b-form-input
                          id="input-3"
                          v-model="match_form.total_available_tickets"
                          :placeholder="match_place_holder.total_available_tickets"
                        ></b-form-input>
                      </b-form-group>
                      <b-form-group id="input-group-4" label="Local id:" label-for="input-3">
                        <b-form-input
                          id="input-4"
                          v-model="match_form.local_id"
                          :placeholder="match_place_holder.local_id"
                        ></b-form-input>
                      </b-form-group>
                      <b-form-group id="input-group-5" label="Visitor id:" label-for="input-3">
                        <b-form-input
                          id="input-5"
                          v-model="match_form.visitor_id"
                          :placeholder="match_place_holder.visitor_id"
                        ></b-form-input>
                      </b-form-group>
                      <b-form-group id="input-group-6" label="Competition id:" label-for="input-3">
                        <b-form-input
                          id="input-6"
                          v-model="match_form.competition_id"
                          :placeholder="match_place_holder.competition_id"
                        ></b-form-input>
                      </b-form-group>
                      <b-button type="submit" variant="primary">Submit</b-button>
                      <b-button type="reset" variant="danger">Reset</b-button>
                      <b-button @click="onDelete()" variant="danger">Delete</b-button>
            </b-form>
          </div>
          <button class="btn btn-secondary btn-lg" style=" margin:2rem" @click="back_match()">Back</button>
        </div>
        </div>
      </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data () {
    return {
      message: 'Compra tus entradas para aprobar la asignatura',
      tickets: 0,
      money: 0,
      matches_added: [],
      matches: [],
      teams: [],
      competitions: [],
      is_showing_cart: false,
      username: '',
      logged: false,
      token: 0,
      is_match_edit: false,
      is_admin: false,
      match: null,
      match_form: {
        id: null,
        date: null,
        price: null,
        total_available_tickets: null,
        local_id: null,
        visitor_id: null,
        competition_id: null
      },
      match_place_holder: {
        price: 'Match price in $',
        total_available_tickets: 'Total available tickets',
        local_id: 'Id of local team',
        visitor_id: 'Id of visitor team',
        competition_id: 'Id of the competition'
      }
    }
  },
  methods: {
    addEventToCart (match) {
      var found = false
      for (var i = 0; i < this.matches_added.length; i++) {
        if (this.matches_added[i].id === match.id) {
          found = true
          this.matches_added[i].quantity = this.matches_added[i].quantity + 1
        }
      }
      if (!found) {
        match.quantity = 1
        this.matches_added.push(match)
      }
      this.tickets += 1
    },
    canAddToCart (match) {
      if (this.is_admin) {
        return true
      }
      if (this.matches_added.length > 0) {
        var found = false
        for (var i = 0; i < this.matches_added.length; i++) {
          if (this.matches_added[i].id === match.id) {
            found = true
            if (match.total_available_tickets - this.matches_added[i].quantity <= 0) {
              return false
            } else {
              return true
            }
          }
        }
        if (!found) {
          return match.total_available_tickets > 0
        }
      } else {
        return match.total_available_tickets > 0
      }
    },
    removeFromCart (match) {
      this.matches_added = this.matches_added.filter(function (m) {
        return m !== match
      })
    },
    canBuy () {
      return this.money > this.cart_total_price()
    },
    increaseQuantity (match) {
      match.quantity += 1
    },
    decreaseQuantity (match) {
      match.quantity -= 1
    },
    matchButtonText (match) {
      if (this.is_admin) {
        return 'Augmentar entrades'
      }
      if (match.total_available_tickets < 1) {
        return 'No queden entrades'
      }

      if (this.matches_added.includes(match)) {
        return 'Afegit a la cistella'
      }

      return 'Afegeix a la cistella'
    },
    match_total_price (match) {
      return match.quantity * match.price
    },
    cart_total_price () {
      let total = 0
      for (const match of this.matches_added) {
        total += this.match_total_price(match)
      }
      return total
    },
    display_price (price) {
      let cents = Math.round(price).toString(10)
      let digits = cents.length
      if (digits === 2) {
        cents = '0' + cents
        digits = 3
      }
      return cents.substring(0, digits - 2) + '.' + cents.substring(digits - 2, digits)
    },
    logcheck () {
      if (this.logged) {
        return 'LogOut'
      } else {
        return 'LogIn'
      }
    },
    loginout () {
      if (this.logged) {
        this.$router.push({path: '/'})
        this.logged = false
        this.username = null
        this.token = null
        this.is_showing_cart = false
        this.is_match_edit = false
        this.matches_added = []
      } else {
        this.$router.push({path: '/userlogin'})
      }
    },
    getTickets (match) {
      var restar = 0
      var matchAppend = null
      for (var i = 0; i < this.matches_added.length; i++) {
        if (this.matches_added[i].id === match.id) {
          restar = this.matches_added[i].quantity
          matchAppend = this.matches_added[i]
        }
      }
      if (this.is_admin) {
        if (restar !== 0) {
          return match.total_available_tickets.toString() + ' + ' + restar
        } else {
          return match.total_available_tickets.toString()
        }
      } else {
        if (match.total_available_tickets - restar >= 0) {
          return (match.total_available_tickets - restar).toString() + '/' + match.total_available_tickets.toString()
        } else {
          this.tickets = this.tickets - match.total_available_tickets - matchAppend.quantity
          matchAppend.quantity = match.total_available_tickets
          restar = match.total_available_tickets
          if (matchAppend.quantity === 0) {
            this.matches_added = this.matches_added.filter(function (m) {
              return m.id !== match.id
            })
          }
          return '0'
        }
      }
    },
    getMatches () {
      this.matches = []
      const pathMatches = 'https://a11-sportsmaster.herokuapp.com/matches'
      const pathCompetition = 'https://a11-sportsmaster.herokuapp.com/competition/'

      axios.get(pathMatches)
        .then((res) => {
          var matches = res.data.matches.filter((match) => {
            return match.competition_id != null
          })
          var promises = []
          for (let i = 0; i < matches.length; i++) {
            const promise = axios.get(pathCompetition + matches[i].competition_id)
              .then((resCompetition) => {
                matches[i].competition = {
                  'name': resCompetition.data.name,
                  'category': resCompetition.data.category,
                  'sport': resCompetition.data.sport
                }
                matches[i].quantity = 0
              })
              .catch((error) => {
                console.error(error)
              })
            promises.push(promise)
          }
          Promise.all(promises).then((_) => {
            this.matches = matches
          })
        })
        .catch((error) => {
          console.error(error)
        })
    },
    toggleCart () {
      if (this.is_showing_cart) {
        this.getMatches()
        var total = 0
        for (const match of this.matches_added) {
          total += match.quantity
        }
        this.tickets = total
      }
      this.is_showing_cart = !this.is_showing_cart
    },
    toggleTextCart () {
      if (this.is_showing_cart) {
        return 'Matches'
      } else {
        return 'Basket (' + this.tickets + ')'
      }
    },
    finishPurchase () {
      if (this.is_admin) {
        for (const match of this.matches_added) {
          var pathA = 'https://a11-sportsmaster.herokuapp.com/match/'
          pathA = pathA + match.id + '/'
          var parametersA = {'total_available_tickets': match.total_available_tickets + match.quantity}
          axios.put(pathA, parametersA, {auth: {username: this.token}})
            .then(() => {
            })
        }
        this.matches_added = []
        this.tickets = 0
        this.getMatches()
        alert('Has afegit entrades correctament!')
        return
      }
      const path = 'https://a11-sportsmaster.herokuapp.com/orders/' + this.username + '/'
      const ids = this.matches_added.map(m => m.id)
      const quantities = this.matches_added.map(m => m.quantity)
      const parameters = {'matches': ids, 'quantities': quantities}
      axios.post(path, parameters, {auth: {username: this.token}})
        .then(() => {
          alert('Compra realitzada correctament')
          this.getMatches()
          this.checkAdminAndMoney()
          this.is_showing_cart = false
          this.tickets = 0
          console.log('Order done')
        })
        .catch((error) => {
          alert('No queden entrades')
          this.getMatches()
          console.log(error)
        })
      this.matches_added = []
    },
    checkAdminAndMoney () {
      alert(this.username)
      alert(this.token)
      const path = 'https://a11-sportsmaster.herokuapp.com/account/' + this.username + '/'
      axios.get(path, {auth: {username: this.token}})
        .then((response) => {
          if (response.data['admin'] === 'Si') {
            this.is_admin = true
          } else {
            this.is_admin = false
          }
          this.money = response.data['money']
        }).catch((error) => {
          alert(error)
          console.error(error)
        })
    },
    editMatch (match) {
      this.getTeams()
      this.getCompetitions()
      this.is_match_edit = true
      if (match === null) {
        this.resetMatch()
        this.match = null
      } else {
        this.match = match
        this.match_form.id = match.id
        this.match_form.date = match.date
        this.match_form.total_available_tickets = match.total_available_tickets
        this.match_form.price = match.price
        this.match_form.local_id = match.local.id
        this.match_form.visitor_id = match.visitor.id
        this.match_form.competition_id = match.competition_id
        this.match_place_holder.price = String(this.match_form.price)
        this.match_place_holder.total_available_tickets = String(this.match_form.total_available_tickets)
        this.match_place_holder.local_id = String(this.match_form.local_id)
        this.match_place_holder.visitor_id = String(this.match_form.visitor_id)
        this.match_place_holder.competition_id = String(this.match_form.competition_id)
      }
    },
    resetMatch () {
      this.match_form.date = null
      this.match_form.total_available_tickets = null
      this.match_form.price = null
      this.match_form.local_id = null
      this.match_form.visitor_id = null
      this.match_form.competition_id = null
      this.match_form.id = null
      this.match_place_holder.price = 'Match price in $'
      this.match_place_holder.total_available_tickets = 'Total available tickets'
      this.match_place_holder.local_id = 'Id of local team'
      this.match_place_holder.visitor_id = 'Id of visitor team'
      this.match_place_holder.competition_id = 'Id of the competition'
    },
    onReset () {
      this.resetMatch()
    },
    onSubmit (e) {
      e.preventDefault()
      if (this.match_form.date === null || this.match_form.total_available_tickets === null || this.match_form.price === null || this.match_form.local_id === null || this.match_form.visitor_id === null) {
        alert('Only competition id can be null')
      } else {
        const parameters = {
          date: this.match_form.date.split('T')[0],
          price: this.match_form.price,
          total_available_tickets: this.match_form.total_available_tickets,
          local_id: this.match_form.local_id,
          visitor_id: this.match_form.visitor_id
        }
        if (this.match_form.competition_id !== null) {
          parameters.competition_id = this.match_form.competition_id
        }
        if (this.match_form.id === null) {
          const path = 'https://a11-sportsmaster.herokuapp.com/match/'
          axios.post(path, parameters, {auth: {username: this.token}})
            .then((res) => {
              this.back_match()
              alert('New match created!')
            })
            .catch((error) => {
              // eslint-disable-next-line
              console.error(error)
              alert('Something gone wrong: ' + error)
            })
        } else {
          const path = 'https://a11-sportsmaster.herokuapp.com/match/' + String(this.match_form.id) + '/'
          axios.put(path, parameters, {auth: {username: this.token}})
            .then((res) => {
              this.back_match()
              alert('Match was edited!')
            })
            .catch((error) => {
              // eslint-disable-next-line
              console.error(error)
              alert('Something gone wrong' + error)
            })
        }
      }
    },
    onDelete () {
      const path = 'https://a11-sportsmaster.herokuapp.com/match/' + String(this.match_form.id) + '/'
      axios.delete(path, {auth: {username: this.token}})
        .then((res) => {
          this.back_match()
          alert(res.data + 'Match deleted successfuly')
        })
        .catch((error) => {
          // eslint-disable-next-line
          this.back_match()
          console.error(error)
          alert('Something gone wrong: ' + error)
        })
    },
    back_match () {
      this.resetMatch()
      this.match = null
      this.getMatches()
      this.is_match_edit = false
    },
    getTeams () {
      this.teams = []
      const pathTeams = 'https://a11-sportsmaster.herokuapp.com/teams/'
      axios.get(pathTeams)
        .then((res) => {
          this.teams = res.data.teams
        })
        .catch((error) => {
          console.error(error)
        })
    },
    getCompetitions () {
      this.competitions = []
      const pathCompetitions = 'https://a11-sportsmaster.herokuapp.com/competitions/'
      axios.get(pathCompetitions)
        .then((res) => {
          this.competitions = res.data.competitions
        })
        .catch((error) => {
          console.error(error)
        })
    },
    pickCompetition (competition) {
      if (this.match_form.competition_id !== null) {
        document.getElementById(this.match_form.competition_id).style.color = 'black'
      }
      this.match_form.competition_id = competition.id
      document.getElementById(competition.id).style.color = 'brown'
    },
    pickLocal (team) {
      if (this.match_form.local_id !== null) {
        document.getElementById('L' + this.match_form.local_id).style.color = 'black'
      }
      this.match_form.local_id = team.id
      document.getElementById('L' + team.id).style.color = 'brown'
    },
    pickVisitor (team) {
      if (this.match_form.visitor_id !== null) {
        document.getElementById('V' + this.match_form.visitor_id).style.color = 'black'
      }
      this.match_form.visitor_id = team.id
      document.getElementById('V' + team.id).style.color = 'brown'
    }
  },
  created () {
    this.logged = this.$route.query.logged === 'true'
    this.username = this.$route.query.username
    this.token = this.$route.query.token
    if (this.logged === undefined) {
      this.logged = false
    }
    this.checkAdminAndMoney()
    this.getMatches()
  }
}

</script>

<style>

.fade-leave-active {
  transition: all 0.5s ease;
}
.fade-leave-to {
  opacity: 0;
}

</style>
