from PIL import Image


class Mapper:
    def __init__(self):
        self.mapColors = {
            # - DEBUG - #
            "000000": "@",
            # - PASSABLE - #
            "59c135": "=", # GRASS
            "9cdb43": ";", # LIGHT GRASS
            "d6f264": "-", # ARID LAND
            "fffc40": ">", # SAND
            "dae0ea": "$", # SNOW
            "4a5462": "+", # STONE
            # - IMPASSABLE - #
            "bb7547": "#", # MOUNTAIN
            "1a7a3e": "M", # TREE
            "143464": "8", # DEEP OCEAN
            "0d397b": "<", # OCEAN
            "154895": "~", # SHALLOW OCEAN
            "285cc4": ".", # SHORE OCEAN
            # - INTERACTABLE - #
            "b4202a": "T", # TOWN
            "9f9f9f": "o", # ENEMY
        }
        
        self.regionColors = {
            "63c74d": "P", # PLAINS
            "3e8948": "F", # FOREST
            "fee761": "D", # DESERT
            "e4a672": "B", # BADLANDS
            "ffffff": "T", # TAIGA
            "0095e9": "M", # MUSHROOM
            "5a6988": "S", # STONE
        }
        
        self.levelColors = {
            "ffffff": "0", # 0-5
            "f2f2f2": "1", # 6-10
            "e6e6e6": "2", # 11-15
            "d9d9d9": "3", # 16-20
            "cccccc": "4", # 21-25
            "bfbfbf": "5", # 26-30
            "b3b3b3": "6", # 31-35
            "a6a6a6": "7", # 36-40
            "999999": "8", # 41-45
            "8c8c8c": "9", # 46-50
            "808080": "a", # 51-55
            "666666": "c", # 61-65
            "1a1a1a": "i", # 91-95
        }
        
        self.imageColors = {
            '0c0c0c': '000', 'c50f1f': '001', '13a10e': '002', 'c19c00': '003', '0037da': '004', '881798': '005', '3a96dd': '006', 'cccccc': '007',
            '767676': '243', 'e74856': '009', '16c60c': '010', 'f9f1a5': '011', '3b78ff': '012', 'b4009e': '013', '61d6d6': '014', 'f2f2f2': '015',
            '000000': '016', '00005f': '017', '000087': '018', '0000af': '019', '0000d7': '020', '0000ff': '021', '005f00': '022', '005f5f': '023',
            '005f87': '024', '005faf': '025', '005fd7': '026', '005fff': '027', '008700': '028', '00875f': '029', '008787': '030', '0087af': '031',
            '0087d7': '032', '0087ff': '033', '00af00': '034', '00af5f': '035', '00af87': '036', '00afaf': '037', '00afd7': '038', '00afff': '039',
            '00d700': '040', '00d75f': '041', '00d787': '042', '00d7af': '043', '00d7d7': '044', '00d7ff': '045', '00ff00': '046', '00ff5f': '047',
            '00ff87': '048', '00ffaf': '049', '00ffd7': '050', '00ffff': '051', '5f0000': '052', '5f005f': '053', '5f0087': '054', '5f00af': '055',
            '5f00d7': '056', '5f00ff': '057', '5f5f00': '058', '5f5f5f': '059', '5f5f87': '060', '5f5faf': '061', '5f5fd7': '062', '5f5fff': '063',
            '5f8700': '064', '5f875f': '065', '5f8787': '066', '5f87af': '067', '5f87d7': '068', '5f87ff': '069', '5faf00': '070', '5faf5f': '071',
            '5faf87': '072', '5fafaf': '073', '5fafd7': '074', '5fafff': '075', '5fd700': '076', '5fd75f': '077', '5fd787': '078', '5fd7af': '079',
            '5fd7d7': '080', '5fd7ff': '081', '5fff00': '082', '5fff5f': '083', '5fff87': '084', '5fffaf': '085', '5fffd7': '086', '5fffff': '087',
            '870000': '088', '87005f': '089', '870087': '090', '8700af': '091', '8700d7': '092', '8700ff': '093', '875f00': '094', '875f5f': '095',
            '875f87': '096', '875faf': '097', '875fd7': '098', '875fff': '099', '878700': '100', '87875f': '101', '878787': '102', '8787af': '103',
            '8787d7': '104', '8787ff': '105', '87af00': '106', '87af5f': '107', '87af87': '108', '87afaf': '109', '87afd7': '110', '87afff': '111',
            '87d700': '112', '87d75f': '113', '87d787': '114', '87d7af': '115', '87d7d7': '116', '87d7ff': '117', '87ff00': '118', '87ff5f': '119',
            '87ff87': '120', '87ffaf': '121', '87ffd7': '122', '87ffff': '123', 'af0000': '124', 'af005f': '125', 'af0087': '126', 'af00af': '127',
            'af00d7': '128', 'af00ff': '129', 'af5f00': '130', 'af5f5f': '131', 'af5f87': '132', 'af5faf': '133', 'af5fd7': '134', 'af5fff': '135',
            'af8700': '136', 'af875f': '137', 'af8787': '138', 'af87af': '139', 'af87d7': '140', 'af87ff': '141', 'afaf00': '142', 'afaf5f': '143',
            'afaf87': '144', 'afafaf': '145', 'afafd7': '146', 'afafff': '147', 'afd700': '148', 'afd75f': '149', 'afd787': '150', 'afd7af': '151',
            'afd7d7': '152', 'afd7ff': '153', 'afff00': '154', 'afff5f': '155', 'afff87': '156', 'afffaf': '157', 'afffd7': '158', 'afffff': '159',
            'd70000': '160', 'd7005f': '161', 'd70087': '162', 'd700af': '163', 'd700d7': '164', 'd700ff': '165', 'd75f00': '166', 'd75f5f': '167',
            'd75f87': '168', 'd75faf': '169', 'd75fd7': '170', 'd75fff': '171', 'd78700': '172', 'd7875f': '173', 'd78787': '174', 'd787af': '175',
            'd787d7': '176', 'd787ff': '177', 'dfaf00': '178', 'dfaf5f': '179', 'dfaf87': '180', 'dfafaf': '181', 'dfafd7': '182', 'dfafff': '183',
            'dfd700': '184', 'dfd75f': '185', 'dfd787': '186', 'dfd7af': '187', 'dfd7d7': '188', 'dfd7ff': '189', 'dfff00': '190', 'dfff5f': '191',
            'dfff87': '192', 'dfffaf': '193', 'dfffd7': '194', 'dfffff': '195', 'ff0000': '196', 'ff005f': '197', 'ff0087': '198', 'ff00af': '199',
            'ff00d7': '200', 'ff00ff': '000', 'ff5f00': '202', 'ff5f5f': '203', 'ff5f87': '204', 'ff5faf': '205', 'ff5fd7': '206', 'ff5fff': '207',
            'ff8700': '208', 'ff875f': '209', 'ff8787': '210', 'ff87af': '211', 'ff87d7': '212', 'ff87ff': '213', 'ffaf00': '214', 'ffaf5f': '215',
            'ffaf87': '216', 'ffafaf': '217', 'ffafd7': '218', 'ffafff': '219', 'ffd700': '220', 'ffd75f': '221', 'ffd787': '222', 'ffd7af': '223',
            'ffd7d7': '224', 'ffd7ff': '225', 'ffff00': '226', 'ffff5f': '227', 'ffff87': '228', 'ffffaf': '229', 'ffffd7': '230', 'ffffff': '231',
            '080808': '232', '121212': '233', '1c1c1c': '234', '262626': '235', '303030': '236', '3a3a3a': '237', '444444': '238', '4e4e4e': '239',
            '585858': '240', '626262': '241', '6c6c6c': '242', '808080': '244', '8a8a8a': '245', '949494': '246', '9e9e9e': '247', 'a8a8a8': '248',
            'b2b2b2': '249', 'bcbcbc': '250', 'c6c6c6': '251', 'd0d0d0': '252', 'dadada': '253', 'e4e4e4': '254', 'eeeeee': '255'
        }
    
    def get_text(self, colors, path, outPath=""):
        image = Image.open(path).convert('RGB')
        W, H = image.size[0], image.size[1]
        aimg = []
        
        for j in range(H):
            aimg.append([])
            for i in range(W):
                r, g, b = image.getpixel((i, j))
                hex = '%02x%02x%02x' % (r, g, b)
                if hex in colors:
                    aimg[j].append(colors[hex])
                else:
                    aimg[j].append(" ")
        
        if outPath:
            with open(outPath, "w+") as mapFile:
                mapFile.truncate(0)
                for line in aimg:
                    mapFile.write(line + "\n")
        
        return aimg
    
    def test(self):
        image = Image.open("image/ansiColorIds.png").convert('RGB')
        W, H = image.size[0], image.size[1]
        counter = 0
        colorIdTable = {}
        
        for j in range(H):
            for i in range(W):
                r, g, b = image.getpixel((i, j))
                hex = '%02x%02x%02x' % (r, g, b)
                colorIdTable.update({hex: str(counter).rjust(3, "0")})
                counter += 1
        
        print(colorIdTable)


mapper = Mapper()
