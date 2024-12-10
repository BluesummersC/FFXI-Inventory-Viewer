--[[
Copyright © 2024 Caleb Bluesummers
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL Giuliano Riccio BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
]]

_addon.name    = 'postBags'
_addon.author  = 'Bluesummers'
_addon.version = '0.5.0'
_addon.commands = {'postbags'}

require('chat')
require('lists')
require('logger')
require('sets')
require('tables')
require('strings')
require('pack')

-- local https = require('ssl.https')

local socket = require("socket")
local try    = socket.try
local ssl    = require("ssl")
local http   = require("socket.http")
local url    = require("socket.url")
local https  = require("ssl.https")


file  = require('files')
slips = require('slips')
config = require('config')
texts = require('texts')
res = require('resources')

json = require('json')

local debug = false
local first_pass             = true
local file_exists            = false

local url_endpoint = "https://bluesummers.pythonanywhere.com/upload_file"

local _M = {
    _VERSION   = "1.0.2",
    _COPYRIGHT = "LuaSec 1.0.2 - Copyright (C) 2009-2021 PUC-Rio",
    PORT       = 443,
    TIMEOUT    = 60
  }

  -- TLS configuration
  local cfg = {
    protocol = "any",
    options  = {"all", "no_sslv2", "no_sslv3", "no_tlsv1"},
    verify   = "none",
  }



local function dump(o)
    if type(o) == 'table' then
       local s = '{ '
       for k,v in pairs(o) do
          if type(k) ~= 'number' then k = '"'..k..'"' end
          s = s .. '['..k..'] = ' .. dump(v) .. ','
       end
       return s .. '} '
    else
       return tostring(o)
    end
 end

function isEmpty(t)
    return next(t) == nil
end

local function sendFindallFile()
    -- Must have the export from findAll in addons/findAll/data/<character_name>.lua>
    if not windower.ffxi.get_info().logged_in then
        print("Must be logged into a character in order to get bag information!")
        return nil
    end
    local player_name   = windower.ffxi.get_player().name
    local findAllFileName = player_name..".lua"
    local file = windower.addon_path.."..\\findAll\\data\\"..findAllFileName


    if windower.file_exists(file) then

        -- Since FindAll outputs a Lua table, we can directly rebuild it here.
        fileT = dofile(file)
        -- spaces in keys plays hell on the jquery table, go ahead and remove it here
        fileT.keyitems = fileT['key items']
        fileT['key items'] = nil

        -- Remove the empty arrays
        for k, v in pairs(fileT) do
            if type(v) == 'table' then
                if isEmpty(v) then
                    fileT[k] = nil
                end
            end
        end

        -- Add some additional info to the table
        local payload = {}
        payload.file_data = fileT
        payload.name = player_name
        payload.passkey = ""

        -- Build a json object using json module from
        --    https://github.com/rxi/json.lua/blob/master/json.lua
        local jsonObj = json.encode(payload)

        -- Call https in order to get the ssl wrapper
        local res, code, response_headers, status, sentUrl = https.request(
            url_endpoint,
            jsonObj
        )
        if res ~= nil then
            print("Response: "..res)
        end
        if code ~= nil then
            print("Code: "..code)
        end
        if status ~= nil then
            print("Status: "..status)
        end
        -- print("url_type: "..dump(sentUrl))
    else
        error("Could not find inventory file for "..player_name)
    end
end


handle_command = function(...)
    if first_pass then
        first_pass = false
        -- log('pre send_command')
        windower.send_command('wait 0.05;postbags '..table.concat({...},' '))
        -- log('post send_command')
    else
        first_pass = true
        local params = L{...}
        local query  = L{}
        local export = nil
        sendFindallFile()

    --     -- convert command line params (SJIS) to UTF-8
    --     for i, elm in ipairs(params) do
    --         params[i] = windower.from_shift_jis(elm)
    --     end

    --     while params:length() > 0 and params[1]:match('^[:!]%a+$') do
    --         query:append(params:remove(1))
    --     end

    --     if params:length() > 0 then
    --         export = params[params:length()]:match('^--export=(.+)$') or params[params:length()]:match('^-e(.+)$')

    --         if export ~= nil then
    --             export = export:gsub('%.csv$', '')..'.csv'

    --             params:remove(params:length())

    --             if export:match('['..('\\/:*?"<>|'):escape()..']') then
    --                 export = nil

    --                 error('The filename cannot contain any of the following characters: \\ / : * ? " < > |')
    --             end
    --         end

    --         query:append(params:concat(' '))
    --     end

    --     search(query, export)
    end
end

windower.register_event('unhandled command', function(command, ...)
    if command:lower() == 'find' then
        local me = windower.ffxi.get_mob_by_target('me')
        if me then
            handle_command(':%s':format(me.name), ...)
        else
            handle_command(...)
        end
    end
end)

windower.register_event('addon command', handle_command)
