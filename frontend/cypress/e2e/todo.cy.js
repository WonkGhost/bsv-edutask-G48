describe('R8 - Todo item tests', () => {

  let uid
  let name
  let email
  let taskId

  before(function () {
    // create a fabricated user from a fixture, code pretty much stolen from login.cy.js
    cy.fixture('user.json')
      .then((user) => {
        cy.request({
          method: 'POST',
          url: 'http://localhost:5000/users/create',
          form: true,
          body: user
        }).then((response) => {
          uid = response.body._id.$oid
          name = user.firstName + ' ' + user.lastName
          email = user.email

          // Create the task once via API
          cy.request({
            method: 'POST',
            url: 'http://localhost:5000/tasks/create',
            form: true,
            body: {
              userid: uid,
              title: 'Test Task',
              url: '123',
              description: 'Test description',
              todos: 'Watch video'
            }
          }).then((response) => {
            taskId = response.body._id ? response.body._id.$oid : response.body[0]._id.$oid
          })
        })
      })
  })

  beforeEach(function () {
    cy.visit('http://localhost:3000')
    cy.contains('div', 'Email Address')
      .find('input[type=text]')
      .type(email)
    cy.get('form').submit()
    cy.get('h1').should('contain.text', 'Your tasks, ' + name)

    // Open the task popup
    cy.get('.container-element a').first().click()
    cy.get('.popup').should('be.visible')
  })

  //TC1 - Fails due to the fact that the submit button is not disabled when the description input is empty. This is a bug that needs to be fixed.
  it('TC1: Add button is disabled when description is empty', () => {
    cy.get('.inline-form input[type=text]').should('have.value', '')
    cy.get('.inline-form input[type=submit]').should('be.disabled')
  })

  //TC2 - Adds a new todo item to the list and checks if it is appended to the end of the list. 
  it('TC2: New todo item is appended to list when description is not empty', () => {
    const description = 'My new todo item'
    cy.get('.inline-form input[type=text]').type(description)
    cy.get('.inline-form input[type=submit]').click()
    cy.get('.todo-list .todo-item').last()
      .should('contain.text', description)
  })

  //TC3 - Toggles the status of a todo item from active to done and checks if the class of the checker element changes from unchecked to checked.
  it('Changes todo status from active to done', () => {
    // Create a new todo item to toggle
    cy.get('.inline-form input[type=text]').type('Toggle test item')
    cy.get('.inline-form input[type=submit]').click()

    // Check that the new item is active (unchecked) before toggling
    cy.get('.todo-list .todo-item').last()
      .find('.checker').should('have.class', 'unchecked')

    // Toggle
    cy.get('.todo-list .todo-item').last()
      .find('.checker').click()

    // Verify
    cy.get('.todo-list .todo-item').last()
      .find('.checker').should('have.class', 'checked')
  })

  //TC4 - Toggles the status of a todo item from done to active and checks if the class of the checker element changes from checked to unchecked.
  it('Changes todo status from done to active', () => {
    cy.get('.todo-list .todo-item').last()
      .find('.checker').should('have.class', 'checked')

    cy.get('.todo-list .todo-item').last()
      .find('.checker').click()

    cy.get('.todo-list .todo-item').last()
      .find('.checker').should('have.class', 'unchecked')
  })

  //TC5 
  it('TC5: Deletes a todo item', () => {
    const description = 'Item to be deleted'
    cy.get('.inline-form input[type=text]').type(description)
    cy.get('.inline-form input[type=submit]').click()
    cy.get('.todo-list .todo-item').its('length').then((lengthBefore) => {
      cy.get('.todo-list .todo-item').last().find('.remover').click()
      cy.get('.todo-list .todo-item').should('have.length', lengthBefore - 1)
    })
  })

  after(function () {
    if (uid) {
      cy.request({
        method: 'DELETE',
        url: `http://localhost:5000/users/${uid}`
      }).then((response) => {
        cy.log('User and all tasks cleared:', response.body)
      })
    }
  })
})