import pytest
from ..model_base_test import ModelBaseTest
from tests.sampleresponse.ewallet import linkaja_payment_response
from xendit.models import EWallet


# fmt: off
class TestCreateLinkAjaPayment(ModelBaseTest):
    @pytest.fixture
    def default_linkaja_payment_data(self):
        tested_class = EWallet
        class_name = "EWallet"
        method_name = "create_linkaja_payment"
        http_method_name = "post"
        items = []
        item = EWallet.helper_create_linkaja_item(
            id="123123", name="Phone Case", price=100000, quantity=1
        )
        items.append(item)

        args = ()
        kwargs = {
            "external_id": "linkaja-ewallet-test-1593505247",
            "phone": "089911111111",
            "amount": 300000,
            "items": items,
            "callback_url": "https://my-shop.com/callbacks",
            "redirect_url": "https://xendit.co/",
            "x_idempotency_key": "test-idemp_123",
        }
        params = (args, kwargs)
        url = "/ewallets"
        expected_correct_result = linkaja_payment_response()
        return (tested_class, class_name, method_name, http_method_name, url, params, expected_correct_result)

    @pytest.fixture
    def api_requestor_request_data(self, default_linkaja_payment_data):
        tested_class, class_name, method_name, http_method_name, url, params, _ = default_linkaja_payment_data
        headers = {"X-IDEMPOTENCY-KEY": "test-idemp_123"}
        body = {
            "external_id": "linkaja-ewallet-test-1593505247",
            "phone": "089911111111",
            "amount": 300000,
            "items": [{"id": "123123", "name": "Phone Case", "price": 100000, "quantity": 1}],
            "callback_url": "https://my-shop.com/callbacks",
            "redirect_url": "https://xendit.co/",
            "ewallet_type": "LINKAJA"
        }
        return (tested_class, class_name, method_name, http_method_name, url, params, headers, body)

    @pytest.mark.parametrize("mock_correct_response", [linkaja_payment_response()], indirect=True)
    def test_return_linkaja_payment_on_correct_params(
        self, mocker, mock_correct_response, default_linkaja_payment_data
    ):
        self.run_success_return_test_on_xendit_instance(mocker, mock_correct_response, default_linkaja_payment_data)

    def test_raise_xendit_error_on_response_error(
        self, mocker, mock_error_request_response, default_linkaja_payment_data
    ):
        self.run_raises_error_test_on_xendit_instance(mocker, mock_error_request_response, default_linkaja_payment_data)

    @pytest.mark.parametrize("mock_correct_response", [linkaja_payment_response()], indirect=True)
    def test_return_linkaja_payment_on_correct_params_and_global_xendit(
        self, mocker, mock_correct_response, default_linkaja_payment_data
    ):
        self.run_success_return_test_on_global_config(mocker, mock_correct_response, default_linkaja_payment_data)

    def test_raise_xendit_error_on_response_error_and_global_xendit(
        self, mocker, mock_error_request_response, default_linkaja_payment_data
    ):
        self.run_raises_error_test_on_global_config(mocker, mock_error_request_response, default_linkaja_payment_data)

    @pytest.mark.parametrize("mock_correct_response", [linkaja_payment_response()], indirect=True)
    def test_send_correct_request_to_api_requestor(self, mocker, mock_correct_response, api_requestor_request_data):
        self.run_send_correct_request_to_api_requestor(mocker, mock_correct_response, api_requestor_request_data)
# fmt: on
