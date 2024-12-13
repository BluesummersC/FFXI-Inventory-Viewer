--[[
Author: Bluesummers
Date: 12/12/2024

]]

_addon.name    = 'armory'
_addon.author  = 'Bluesummers'
_addon.version = '0.8.0'
_addon.commands = {'armory'}

require('logger')
require('tables')
require('strings')

local https  = require("ssl.https")

file  = require('files')
texts = require('texts')
res = require('resources')

-- non-lib json
json = require('json')

local debug = false
local first_pass = true

local url = "https://bluesummers.pythonanywhere.com"
local url_endpoint = url.."/upload_file"


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


local function sendFindallFile()
    -- Must have the export from findAll in addons/findAll/data/<character_name>.lua>
    if not windower.ffxi.get_info().logged_in then
        print("Must be logged into a character in order to get bag information!")
        return nil
    end

    local player_name   = windower.ffxi.get_player().name
    local file = windower.addon_path.."..\\findAll\\data\\"..player_name..".lua"

    if windower.file_exists(file) then

        -- Since FindAll outputs a Lua table, we can directly rebuild it here.
        fileT = dofile(file)
        -- spaces in keys plays hell on the jquery table, go ahead and remove it here
        fileT.keyitems = fileT['key items']
        fileT['key items'] = nil

        -- Remove the arrays of empty storage locations
        for k, v in pairs(fileT) do
            if type(v) == 'table' then
                if next(v) == nil then
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

        print("Processing...")
        -- Call https in order to get the ssl wrapper
        local res, code, response_headers, status = https.request(url_endpoint, jsonObj)
        if res ~= nil and string.find(res, "name") and string.find(res, "passkey") then
            if debug then print("(Debug) Response: "..res) end

            -- make it a table
            local tosplit = string.gsub(res, '"', '')
            local sub = string.sub(tosplit, 2, #tosplit-2 )
            if debug then print("(Debug) Sub: "..sub) end
            local namepass = {}
            for k, v in string.gmatch(sub, "(%w+):(%w+)") do
                namepass[k] = v
            end

            local link = url..'?name='..namepass.name..'&passkey='..namepass.passkey
            print('URL sent to clipboard:')
            print('   '..link)
            windower.copy_to_clipboard(link)
        else
            print('ERROR: Failed to get result from database!')
            if debug then print("(Debug) Response: "..res) end
        end

        if code ~= nil then
            if debug then print("(Debug) Code: "..dump(code)) end
        end

        if status ~= nil then
            if debug then print("(Debug) Status: "..dump(status)) end
        end

    else
        print("ERROR: Could not find inventory file for "..player_name)
    end
end


handle_command = function(...)
    if first_pass then
        first_pass = false
        -- Is this needed?
        windower.send_command('wait 0.05;armory '..table.concat({...},' '))
    else
        first_pass = true
        local params = L{...}
        debug = false

        -- convert command line params (SJIS) to UTF-8
        for i, elm in ipairs(params) do
            params[i] = windower.from_shift_jis(elm)
        end

        if params:length() > 0 then
            arg = params[params:length()]:match('^--debug$') or params[params:length()]:match('^-d$')
            if arg ~= nil then
                print('(Debug is true)')
                debug = true
            end

            params:remove(params:length())
        end

        sendFindallFile()
    end
end

windower.register_event('addon command', handle_command)
