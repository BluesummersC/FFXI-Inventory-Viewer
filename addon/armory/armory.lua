--[[
Copyright © 2024, Caleb Bluesummers
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of armory nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL Caleb Bluesummers BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

]]

_addon.name    = 'armory'
_addon.author  = 'Bluesummers'
_addon.version = '0.8.0'
_addon.commands = {'armory'}

require('logger')
require('tables')
require('strings')

local https  = require("ssl.https")
local http = require("socket.http")

require('files')
require('texts')
require('resources')

-- non-lib json
json = require('json')

debug = false
local first_pass = true

local url = "https://bluesummers.pythonanywhere.com"
local url_endpoint = url.."/upload_file"


function dump(o)
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

-- local co = coroutine.wrap( function(endpoint, body)
--     local res, code, response_headers, status = https.request(endpoint, body)
--     return res, code, response_headers, status
-- end)
function urlUp(url)
    local res, code, response_headers, status = http.request(url)
    if code ~= 200 then
        return false
    else
        return true
    end
end

local function sendFindallFile(passkey)
    -- Must have the export from findAll in addons/findAll/data/<character_name>.lua>
    if not windower.ffxi.get_info().logged_in then
        print("Must be logged into a character in order to get bag information!")
        return nil
    end

    local player_name   = windower.ffxi.get_player().name
    local file = windower.addon_path.."..\\findAll\\data\\"..player_name..".lua"

    if windower.file_exists(file) == false then
        print("ERROR: Could not find inventory file for "..player_name". Run FindAll's export option to create it.")
        return nil
    end

    print("Processing "..player_name..".lua".."...")
    -- Since FindAll outputs a Lua table, we can directly rebuild it here.
    local fileT = dofile(file)
    -- spaces in keys plays hell on the jquery table, go ahead and remove it here
    fileT.keyitems = fileT['key items']
    fileT['key items'] = nil

    -- Remove the arrays of empty storage locations
    local cnt = 0
    for k, v in pairs(fileT) do
        cnt = cnt + 1
        if type(v) == 'table' then
            if next(v) == nil then
                fileT[k] = nil
            end
        end
    end

    if cnt == 0 then
        print('ERROR: No data in FindAll file. Try to export your inventory from FindAll again.')
        return nil
    end

    -- Add some additional info to the table
    local payload = {}
    payload.file_data = fileT
    payload.name = player_name
    payload.passkey = passkey

    -- Build a json object using json module from
    --    https://github.com/rxi/json.lua/blob/master/json.lua
    local jsonObj = json.encode(payload)
    local co = coroutine.wrap( function(endpoint, body)
        local res, code, response_headers, status = https.request(endpoint, body)
        return res, code, response_headers, status
    end)

    if not urlUp(url) then
        print('ERROR: Could not connect to site: '..url)
        return nil
    end

    print("Sending inventory data to server...")
    -- Call https in order to get the ssl wrapper
    local res = nil
    local code = nil
    local response_headers = nil
    local status = nil

    res, code, response_headers, status = co(url_endpoint, jsonObj)

    if debug then print("(Debug) Response: "..dump(res)) end
    if debug then print("(Debug) Code: "..code) end
    -- if debug then print("(Debug) Status: "..dump(status)) end

    if code ~= 200 then
        print('ERROR: : '..code)
        return nil
    end

    local namepassT = {}
    if not res:find("name") or not res:find("passkey") then
        print('ERROR: Database failed to return a name or passkey!')
        return nil
    else
        namepassT = json.decode(res)
    end

    if namepassT.name == nil or namepassT.passkey == nil then
        print('ERROR: Could not get the name and passkey from the returned string')
        return nil
    end

    local link = url..'?name='..namepassT.name..'&passkey='..namepassT.passkey
    print('Success! Opening URL to '..link)
    windower.open_url(link)

end


local handle_command = function(...)
    if first_pass then
        first_pass = false
        -- Is this needed?
        windower.send_command('wait 0.05;armory '..table.concat({...},' '))
    else
        local params = L{...}
        first_pass = true
        debug = false
        local passkey = ""

        -- convert command line params (SJIS) to UTF-8
        params:map(windower.from_shift_jis)

        for _, param in ipairs(params) do
            if S{'--debug', '-d'}:contains(param) then
                debug = true
                print('(Debug is true)')
            elseif param:match('%w') then
                if #param ~= 8 then
                    print('ERROR: Optional Passkey must be 8 digits long')
                    return nil
                end
                passkey = param
                print('(Using passkey: '..param..')')
            else
                print('else: '..param)
            end
        end

        sendFindallFile(passkey)
    end
end

windower.register_event('addon command', handle_command)
-- windower.register_event('addon command', function(...)
--     local params = L{...}

-- end)
