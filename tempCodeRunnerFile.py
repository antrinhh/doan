
                    if text != "unknown":
                        x, y, z = trans_end_zones.flatten()
                        if text == "red":
                            arduino.send_command(x, y, z, 1, 1)
                        if text == "blue":
                            arduino.send_command(x, y, z, 1, 2)
                        if text == "green":
                            arduino.send_command(x, y, z,