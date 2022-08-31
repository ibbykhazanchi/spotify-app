import express, {Request, Response, Application} from 'express'
import request from 'request'
import { URLSearchParams } from 'url';
import { generateRandomString } from './utils'
import cors from 'cors'
import cookieParser from 'cookie-parser'

const app : Application = express()
app.use(cors())
   .use(cookieParser())
const PORT = process.env.PORT || 8888

const client_id = 'f053414153564cd98f1bb34f8ac9a0ca'; // Your client id
const client_secret = '7ff0b650b83949d2aa43a0df42e48a2e'; // Your secret
const redirect_uri = 'http://localhost:8888/callback'; // Your redirect uri
const stateKey = 'spotify_auth_state'

app.listen(PORT, (): void => {
    console.log(`Server Running here 👉 https://localhost:${PORT}`)
})

app.get('/', (req: Request, res: Response): void => {
    res.cookie('pishab', "hi")
    res.send("Hello Typescript with node.js")
})

app.get('/login', (req: Request, res: Response): void => {
    const state = generateRandomString(16)
    res.cookie(stateKey, state)

    const scope = 'user-read-private user-read-email'

    const searchParams = new URLSearchParams({
        response_type: 'code',
        client_id: client_id,
        scope: scope,
        redirect_uri: redirect_uri,
        state: state
    })
    res.redirect(
        'https://accounts.spotify.com/authorize?' +
        searchParams.toString()
    )
})

app.get('/callback', (req: Request, res: Response): void => {
    const code = req.query.code || null
    const state = req.query.state || null
    const storedState = req.cookies ? req.cookies[stateKey] : null
        

    if(state == null || state !== storedState){
        const errorParams = new URLSearchParams({
            error: 'state_mismatch'
        })

        res.redirect('/#' + errorParams.toString())
    } else {
        res.clearCookie(stateKey)
        const authOptions = {
            url: 'https://accounts.spotify.com/api/token',
            form: {
              code: code,
              redirect_uri: redirect_uri,
              grant_type: 'authorization_code'
            },
            headers: {
              'Authorization': 'Basic ' + (Buffer.from(client_id + ':' + client_secret).toString('base64'))
            },
            json: true 
        }

        request.post(authOptions, (error: any, response : request.Response, body: any) => {
            if(!error && response.statusCode === 200){
                console.log("good")
                const access_token = body.access_token
                const refresh_token = body.refresh_token

                const options = {
                    url: 'https://api.spotify.com/v1/me',
                    headers: { 'Authorization': 'Bearer ' + access_token },
                    json: true 
                }

                request.get(options, (error: any, response : request.Response, body: any) => {
                    console.log(body)
                    res.send(body)
                })
            } else {
                console.log("bad")
                const errorParams = new URLSearchParams({
                    error: 'invalid_token'
                })
        
                res.redirect('/#' + errorParams.toString())
            }
        })
    }

})

app.get('/refresh_token', (req: Request, res: Response): void => {
    const refresh_token = req.query.refresh_token
    const authOptions = {
      url: 'https://accounts.spotify.com/api/token',
      headers: { 'Authorization': 'Basic ' + (Buffer.from(client_id + ':' + client_secret).toString('base64')) },
      form: {
        grant_type: 'refresh_token',
        refresh_token: refresh_token
      },
      json: true
    }

    request.post(authOptions, (error: any, response : request.Response, body: any) => {
        if (!error && response.statusCode === 200) {
          const access_token = body.access_token
          res.send({
            'access_token': access_token
          })
        }
    })
})
