import requests


class FACEITBot:
    """
  A class to access the FACEIT API in order to download data.

  This class features can access various parts of the FACEIT API and download the result.

  Attributes:
    api_key (str): the key used by this project to access the FACEIT API.
    base_url (str): Base URL to access the FACEIT databank.
    data (dict): the data acquired by using the query function. Only stores most recent query data.

  """

    def __init__(self):
        """
    Initialize the FACEIT Bot. Sets up empty data, and base url of database.
    """
        self.api_key = "7b27241b-ff39-49aa-a58e-84ba832293aa"
        self.base_url = "https://open.faceit.com/data/v4/"
        self.data = []
        return

    def query(self, endpoint, item_id, offset=0, limit=50):

        """
      Send a query to the FACEIT databank and download the results.
      Returns None if successful, Error String if failed

        Args:
          endpoint (str): endpoint to connect to, i.e. "championships"
          item_id (str): unique id of the item to be accessed
          offset (int, optional): offset in databank where to start the download. Defaults to 0.
          limit (int, option): how many datapoints to download. Defaults to 50. Maximum 100.

        Notes:
        This function updates the internal .data attribute. Remember to limit API rates as much as possible.
    """

        #setup complete url out of endpoint, id, etc

        compl_url = f"{self.base_url}/{endpoint}/{item_id}"

        #setup parameters and headers(authentication)

        params = {
            "limit": limit,
            "offset": offset
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        }

        #get response, if successful process json file

        response = requests.get(compl_url, params=params, headers=headers)
        if response.status_code == 200:
            self.data = response.json()
            print("Successfull request")
            return None
        else:
            return f"Error, {response.status_code}, {response.text}"
