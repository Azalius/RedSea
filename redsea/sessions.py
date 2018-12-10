from redsea.tidal_api import TidalSessionFile, TidalRequestError


class SimpleSessionFile(TidalSessionFile):
    ''' An extra easy & simple way to deal with tidal auth'''

    def new_session(self, session_name, username, password):

        try:
            try:super().remove("default")
            except: pass
            super().new_session("default", username, password)
        except TidalRequestError as e:
            if str(e).startswith('3001'):
                raise Exception('Username or password incorrect. Please try again.')
        except Exception as e: raise e
        else:
            print("Authentication done. You won't need to enter your id and password again.")

    def load_session(self):
        '''
        Loads default session from session store
        '''

        try:
            return super().load(session_name="default")

        except ValueError as e:
            raise Exception("It appears that you never authenticated. Please do so by adding '-id ID -pwd PWD' to your command.")

    def get_session(self):
        ''' Get the session'''
        return self.sessions[self.default]
